from dotenv import load_dotenv
load_dotenv()


import functions.article_generator
# from functions.chat import chat

# while True:
#     message = input("You: ")
#     print("THT:", chat(message))

# from langchain.utilities import ApifyWrapper
# from langchain.document_loaders.base import Document

# apify = ApifyWrapper()

# loader = apify.call_actor(
#     actor_id="apify/website-content-crawler",
#     run_input={"startUrls": [{"url": "https://python.langchain.com/en/latest/"}]},
#     dataset_mapping_function=lambda item: Document(
#         page_content=item["text"] or "", metadata={"source": item["url"]}
#     ),
# )
    
