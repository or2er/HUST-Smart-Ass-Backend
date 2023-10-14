from langchain.document_loaders import WikipediaLoader
from langchain.docstore.document import Document
from .knowledge_graph import diffbot_nlp

document = Document(
  page_content = """
  Donald John Trump (born June 14, 1946) is an American politician, media personality, and businessman who served as the 45th president of the United States from 2017 to 2021.

  Trump graduated from the University of Pennsylvania with a bachelor's degree in economics in 1968. He became president of his father's real-estate business in 1971 and renamed it the Trump Organization. He expanded its operations to building and renovating skyscrapers, hotels, casinos, and golf courses and later started side ventures, mostly by licensing his name. From 2004 to 2015, he co-produced and hosted the reality television series The Apprentice. He and his businesses have been plaintiff or defendant in more than 4,000 state and federal legal actions, including six business bankruptcies.

  Trump won the 2016 presidential election as the Republican nominee against Democratic nominee Hillary Clinton while losing the popular vote.[a] During the campaign, his political positions were described as populist, protectionist, isolationist, and nationalist. His election and policies sparked numerous protests. He was the first U.S. president with no prior military or government service. The 2017–2019 special counsel investigation established that Russia interfered in the 2016 election to favor his campaign. Trump promoted conspiracy theories and made many false and misleading statements during his campaigns and presidency, to a degree unprecedented in American politics. Many of his comments and actions have been characterized as racially charged or racist and many as misogynistic.
  """,
  metadata={"source":"local"}
)

raw_documents = [
    document
]

graph_documents = diffbot_nlp.convert_to_graph_documents(raw_documents)

print(graph_documents)