from langchain.prompts import PromptTemplate
from langchain.llms import CTransformers
from langchain.chains import RetrievalQA
from utils.prompt import prompt_template
from utils.vector import Vector


class ConfigLangChain:

    promt = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    def __init__(self, model_folder, max_token, temperature, vector_instance) -> None:

        self.index_name = vector_instance.index
        self.chain_type_args = {"prompt": self.promt}
        self.llm = CTransformers(
            model=model_folder,
            model_type="llama",
            config={"max_new_tokens": max_token, "temperature": temperature},
        )

        self.qa = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=vector_instance.retrieve(self.index_name).as_retriever(
                search_kwargs={"k": 1}
            ),
            return_source_documents=True,
            chain_type_kwargs=self.chain_type_args,
        )

    def question_answer(self, question: str):
        return self.qa({"query": question})
