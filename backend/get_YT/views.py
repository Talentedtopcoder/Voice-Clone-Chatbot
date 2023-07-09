from django.shortcuts import render
from django.http import JsonResponse
from youtube_transcript_api import YouTubeTranscriptApi
import googleapiclient.discovery
from tqdm import tqdm
import traceback
import pinecone

# import pinecone
import openai
from pathlib import Path
import json

# Create your views here.


def get_YT_TS(request):
    if request.method == "GET":
        try:
            channel_id = "UCQM4dR3UREnGIHz93zRw_0Q"
            video_ids = get_ids(channel_id)[:20]
            yt_ts = get_transcripts(video_ids)
            write_to_file(yt_ts)
            return JsonResponse({"message": "success"})
        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({"message": "failed"})


# making embedding from youtube.txt
def creating_embedding(request):
    if request.method == "GET":
        try:
            text = load_text("./media/YouTube.txt")
            content = split_text(text, 5)
            embedding, vector_ids, metadata = text_to_embedding(content)

            embedding_to_pinecone(metadata, embedding, vector_ids)

            return JsonResponse({"content": "success"})
        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({"content": "failed"})


# make embedding
def make_embedding(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            channel_id = data.get("channel_id")
            video_ids = get_ids(channel_id)[:20]
            yt_ts = get_transcripts(video_ids)
            write_to_file(yt_ts)
            text = load_text("./media/YouTube.txt")
            content = split_text(text, 5)
            embedding, vector_ids, metadata = text_to_embedding(content)

            embedding_to_pinecone(metadata, embedding, vector_ids)

            return JsonResponse({"content": "success"})
        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({"content": "failed"})


# get video ids and convert to file
def get_ids(channel_id):
    api_key = "AIzaSyDn0w7tNmCNmYzKannlmShUOvwVxD3HgPc"  # @param {type:"string"}

    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

    video_ids = []
    page_token = None

    while True:
        request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            maxResults=50,  # Fetch 50 videos at a time
            pageToken=page_token,  # Add pagination
        )
        response = request.execute()

        video_ids += [
            item["id"]["videoId"]
            for item in response["items"]
            if item["id"]["kind"] == "youtube#video"
        ]

        # Check if there are more videos to fetch
        if "nextPageToken" in response:
            page_token = response["nextPageToken"]
        else:
            break
    return video_ids


def get_transcripts(video_ids):
    transcripts = []
    print(video_ids)
    for video_id in tqdm(video_ids):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            transcripts.append(transcript)
        except Exception as ex:
            print(f"An error occurred for video: {video_id} [{ex}]")
    return transcripts


def write_to_file(transcripts):
    with open("YouTube.txt", "w") as f:
        for transcript in transcripts:
            for item in transcript:
                f.write(item["text"] + "\n")


# clean the transcript
def load_text(input_path):
    with Path(input_path).open("r") as file:
        return file.read()


def split_text(input_text, chunk_number):
    text_list = input_text.split("\n")
    index = 0
    content = []
    sentence = ""
    for element in text_list:
        print(element)
        index += 1
        sentence += f"\n {element}"
        if index % chunk_number == 0:
            content.append(sentence)
            sentence = ""
            index = 0

    return content


def text_to_embedding(content_list):
    api_key = (
        "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"  # @param {type:"string"}
    )
    openai.api_key = api_key
    try:
        res = openai.Embedding.create(
            model="text-embedding-ada-002", input=content_list
        )
        embedding = []
        vect_id = []
        index = -1
        content = []
        for element in res["data"]:
            index += 1
            embedding.append(element["embedding"])
            vect_id.append(f"vect {index}")
            content.append({"sentence": content_list[index]})
        return embedding, vect_id, content
    except Exception as e:
        print(traceback.format_exc())
        return [], []


def embedding_to_pinecone(content_list, embedding, vector_ids):
    try:
        vector = list(zip(vector_ids, embedding, content_list))
        # print(vector)
        pinecone_api_key = "07658eb7-e904-434f-98e2-601c133c5165"
        pinecone_env = "us-west4-gcp-free"
        pinecone.init(api_key=pinecone_api_key, environment=pinecone_env)
        index_list = pinecone.list_indexes()
        print(index_list)
        pine_index = pinecone.Index(index_list[0])
        chunk = []
        index = 0
        for i in vector:
            index += 1
            chunk.append(i)
            if index % 50 == 0:
                print(index)
                pine_index.upsert(vectors=chunk, namespace="example-namesapce")
                chunk = []
        return "success"
    except Exception as e:
        print(traceback.format_exc())
        return "failed"
