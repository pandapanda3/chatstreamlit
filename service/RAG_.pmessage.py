import time
import numpy as np
import faiss
# from openai.embeddings_utils import get_embedding#, cosine_similarity
from sklearn.metrics.pairwise import cosine_similarity
import re
import tiktoken
import pickle
import os
from openai import OpenAI
client = OpenAI()

# key写在这里
os.environ['OPENAI_API_KEY'] = "" 

class VectorDatabase:
    def __init__(self, max_length=30, dimension=1536):
        self.dimension = dimension
        # self.index = faiss.IndexFlatL2(dimension)  # 使用L2距离创建FAISS索引
        self.index = faiss.IndexFlatIP(dimension)  # 使用L2距离创建FAISS索引
        self.texts = []  # 存储文本单位
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        self.max_length = max_length # 每个片段最大长度

    def reset(self):
        self.index = faiss.IndexFlatIP(self.dimension)

    def save_faiss(self, path):
        faiss.write_index(self.index, path)

    def load_faiss(self, path):
        self.index = faiss.read_index(path)

    def save_texts(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self.texts, f)
    def load_texts(self, path):
        with open(path, 'rb') as f:
            self.texts = pickle.load(f)

    def _get_embedding(self, text):
        count = 0
        while count < 3:
            embedding = client.embeddings.create(input = [text], model='text-embedding-ada-002').data[0].embedding
            try:
                embedding = client.embeddings.create(input = [text], model='text-embedding-ada-002').data[0].embedding
                break

            except:
                time.sleep(3)
                count += 1
        embedding = np.array(embedding)
        embedding = embedding.reshape(1, -1)

        return embedding

    def merge_strings_until_max_length(self, strings, max_length, index):
        merged_list = []  # 初始化合并后的字符串
        for i in range(len(strings)):
            # 检查添加下一个字符串是否会超过最大长度
            if len(self.tokenization(''.join(merged_list))) + len(self.tokenization(strings[i])) > max_length:
                break  # 如果超过最大长度，停止合并
            merged_list.append(strings[i])

        # 下面的代码是按照原来的顺序拼好
        # 例如对一一段话[0,1,2,3,4,5], 按照相关程度排序是[5,3,4,0,1,2],为了不超过最大长度只能截取[5,3,4]
        # 为了保证语义连贯，把这个句子的顺序调整为[3,4,5]
        index = index[:len(merged_list)]
        index_2 = [sorted(index).index(x) for x in index]
        original_order = sorted(enumerate(merged_list), key=lambda x: index_2[x[0]])
        restored_sentences = [sentence for i, sentence in original_order]
        return ''.join(restored_sentences),restored_sentences

    def tokenization(self, text):
        return self.encoding.encode(text)  # 简化：按字符分割

    def add_text(self, text, split=True):
        """添加新文本并计算其嵌入向量，然后将向量添加到FAISS索引中"""
        if split:
            segments = self.split_text(text, self.max_length)
            for sentence in segments:
                embedding = self._get_embedding(sentence)
                if self.index.is_trained:
                    self.index.add(embedding)  # 向索引中添加向量
                self.texts.append(sentence)
        else:
            embedding = self._get_embedding(text)
            if self.index.is_trained:
                self.index.add(embedding)
            self.texts.append(text)

    def query_length(self, query_text, max_length, threshold=0.5, return_list=False):
        """给定查询，返回最相关的文本单位"""
        query_embedding = self._get_embedding(query_text)
        D, I = self.index.search(query_embedding, 99999)  # 执行搜索

        # 过滤掉相关性分数低于阈值的文本单位
        filtered_results = [(self.texts[i], D[0][j]) for j, i in enumerate(I[0]) if D[0][j] >= threshold and i >= 0]

        if not filtered_results:
            return '' if not return_list else []

        # 提取过滤后的句子和对应的索引
        relative_sentences = [text for text, _ in filtered_results]
        index = [i for i, _ in filtered_results]

        # 合并字符串直到最大长度
        text, text_list = self.merge_strings_until_max_length(strings=relative_sentences, max_length=max_length, index=index)

        if return_list:
            return text_list
        return text


    def query_num(self, query_text, num, threshold=0.5, return_list=False):
        """给定查询，返回最相关的文本单位"""
        query_embedding = self._get_embedding(query_text)
        D, I = self.index.search(query_embedding, 99999)  # 执行搜索

        # 过滤掉相关性分数低于阈值的文本单位
        filtered_results = [(self.texts[i], D[0][j]) for j, i in enumerate(I[0]) if D[0][j] >= threshold and i >= 0]

        if not filtered_results:
            return '' if not return_list else []

        # 提取过滤后的句子
        relative_sentences = [text for text, _ in filtered_results]

        if len(relative_sentences) < num:
            return ''.join(relative_sentences) if not return_list else relative_sentences

        relative_sentences = relative_sentences[:num]

        # 下面的代码是按照原来的顺序拼好
        # 例如对一段话[0,1,2,3,4,5], 按照相关程度排序是[5,3,4,0,1,2],为了不超过最大长度只能截取[5,3,4]
        # 为了保证语义连贯，把这个句子的顺序调整为[3,4,5]
        index = relative_sentences[:num]
        index_2 = [sorted(index).index(x) for x in index]
        original_order = sorted(enumerate(relative_sentences), key=lambda x: index_2[x[0]])
        restored_sentences = [sentence for i, sentence in original_order]

        if return_list:
            return restored_sentences
        return ''.join(restored_sentences)

    def find_sentences(self, text):
        """
        根据句子界定符号分割文本为句子列表，同时保留分隔符。
        支持中文和英文的界定符。
        """
        # 使用正则表达式分割，但保留分隔符
        sentence_endings = r'([。？！.?!\n]+)'
        sentences = re.split(sentence_endings, text)
        # 将分隔符与前面的句子合并
        sentences = [sentences[i] + sentences[i+1] for i in range(0, len(sentences)-1, 2)]
        sentences = [i.strip() for i in sentences]
        sentences = [i for i in sentences if i != '']
        return sentences

    def split_text(self, text, max_length):
        sentences = self.find_sentences(text)
        segments = []  # 存储最终的文本段
        current_segment = []  # 当前正在构建的段
        current_length = 0  # 当前段的长度

        for sentence in sentences:
            # 估计当前句子的token长度
            sentence_length = len(self.tokenization(sentence))
            if sentence_length > max_length:
                # 如果句子长度本身就超过最大长度，将其作为一个独立的段落
                if current_segment:
                    segments.append(''.join(current_segment))  # 先添加当前正在构建的段
                    current_segment = []  # 重置当前段
                    current_length = 0
                segments.append(sentence)  # 添加超长句子作为独立段落
            elif current_length + sentence_length <= max_length:
                # 如果当前句子可以加入当前段
                current_segment.append(sentence)
                current_length += sentence_length
            else:
                # 如果当前句子加入会超过最大长度，先结束当前段
                segments.append(''.join(current_segment))  # 将句子合并为一个段落
                current_segment = [sentence]  # 开始新的段
                current_length = sentence_length

        # 不要忘记添加最后一个段
        if current_segment:
            segments.append(''.join(current_segment))

        return segments

if __name__ == '__main__':
    # 示例使用
    # 给每一个病人都创建新的数据库，防止数据混在一起
    db = VectorDatabase(max_length=100)
    text = """
    Dentist: "Have you been experiencing any sensitivity when eating or drinking hot or cold foods and beverages?"
    Patient: "Yes, actually. For the past couple of weeks, I've noticed a sharp pain in my lower right back tooth whenever I drink something cold. It usually lasts for a few seconds and then goes away. It's not constant, but it's definitely uncomfortable when it happens. I've been trying to avoid cold drinks because of it, but sometimes I forget and the pain catches me off guard."
    """
    # 添加文本 - 每一次对话的问和答都储存进来
    db.add_text(text)
    # 搜索相关文本 - 每次一次prompt的时候，都从数据库里搜索相关的文本出来
    db.query_num("The location of the problem", 10, 0.1,True)






st.title('1History Conversation')
user_info = st.session_state.user_info
user_id = user_info['user_id']
role = user_info['role']


chat_history_data = fetch_chat_history_data(user_id, role)

chat_history_data_df = pd.DataFrame(chat_history_data,
                                    columns=["number", "publish"])

col1, col2 = st.columns([5, 1])

with col1:

    # Display the data in Streamlit
    st.data_editor(
        chat_history_data_df,
        column_config={
            "number": st.column_config.NumberColumn(
                "The number of chat session",
                help="The number of chats",
                width="small"
            ),
            "publish": st.column_config.TextColumn(
                "Publish",
                help="The name of the user",
                width="medium"
            ),
    )

with col2:
    # when click the button, jump to another page to get the detail message
    for index, row in chat_history_data_df.iterrows():
        session_id = row["session_id"]
        chat_count = row["chat_count"]
        if st.button(f"Click me to jump into chat session: {chat_count}", key=f'{chat_count}_{session_id}'):
            st.session_state.session_id = session_id
            st.session_state.chat_count = chat_count
            st.switch_page("pages/2History Detail Conversation.py")