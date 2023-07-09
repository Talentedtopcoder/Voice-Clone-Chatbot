from django.shortcuts import render
from django.http import JsonResponse
from youtube_transcript_api import YouTubeTranscriptApi
import googleapiclient.discovery
from tqdm import tqdm
import traceback
import pinecone
import json

from langchain.chat_models import ChatOpenAI
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.chains import RetrievalQA
from langchain.vectorstores import Pinecone
from django.http import JsonResponse
import openai

OPENAI_API_KEY = "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"


def get_answer(request):
    if request.method == "POST":
        data = json.loads(request.body)
        message = data.get("message")
        embedding = creating_embedding([message])
        contents = query_embedding(embedding)
        summary = summary_contents(contents)

        result = get_result(summary, message)

        return JsonResponse({"message": result})


def creating_embedding(query):
    api_key = (
        "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"  # @param {type:"string"}
    )
    openai.api_key = api_key
    try:
        res = openai.Embedding.create(model="text-embedding-ada-002", input=query)
        embedding = []
        vect_id = []
        index = -1
        for element in res["data"]:
            index += 1
            embedding.append(element["embedding"])
            vect_id.append(f"vect {index}")
        return embedding[0]
    except Exception as e:
        print(traceback.format_exc())
        return []


def query_embedding(query_embedding):
    pinecone_api_key = "07658eb7-e904-434f-98e2-601c133c5165"
    pinecone_env = "us-west4-gcp-free"
    pinecone.init(api_key=pinecone_api_key, environment=pinecone_env)
    index_list = pinecone.list_indexes()
    print(index_list)
    Index = pinecone.Index(index_list[0])
    print(query_embedding)
    contents = Index.query(
        vector=query_embedding,
        top_k=10,
        include_metadata=True,
        namespace="example-namesapce",
    )

    return contents["matches"]


def summary_contents(contents):
    summary = ""
    for i in contents:
        print(i)
        summary += i["metadata"]["sentence"]

    return summary


def get_result(summary, query):
    api_key = "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"
    openai.api_key = api_key
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": summary},
            {"role": "user", "content": query},
        ],
    )
    result = res["choices"][0]["message"]["content"]
    return result
