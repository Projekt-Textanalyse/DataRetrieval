# -*- coding: utf-8 -*-

# Sample Python code for youtube.search.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python

import os
import json
import code

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# method recursively gets all comment ids 
def get_ids(youtube, videoId):

    # list for storing ids
    ids = []

    # request for first page
    request = youtube.commentThreads().list(
        part="id",
        videoId=videoId
    )
    response = request.execute()

    # append ids to list
    for comment in response.get('items'):
        ids.append(comment.get('id'))

    
    nextPageToken = response.get('nextPageToken')
    # as long as there is a page token, query next page and save comments to list
    while nextPageToken:
        request = youtube.commentThreads().list(
            part="id",
            pageToken=nextPageToken,
            videoId=videoId
        )

        response = request.execute()

        # append ids to list
        for comment in response.get('items'):
            ids.append(comment.get('id'))
        
        nextPageToken = response.get('nextPageToken')

    return ids

# function that gets all comments by id and saves them in a dict
def get_comments(youtube, commentIds, videoId):

    comments = []

    for commentId in commentIds:

        request = youtube.comments().list(
            part="snippet",
            id=commentId
        )
        try:
            response = request.execute()
        except:
            break

        comment = {
            'id' : commentId,
            'text': response.get('items')[0].get('snippet').get('textOriginal'),
            'date': response.get('items')[0].get('snippet').get('publishedAt')
        }

        comments.append(comment)

    commentDict = {
        "videoId": videoId,
        "comments": comments
    }

    return commentDict






def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret_700680253582-0i0aaa2j18r2s79kneouenku9gpv7ftv.apps.googleusercontent.com.json"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    ids = get_ids(youtube, "6Af6b_wyiwI")
    print(len(ids))
    commentDict = get_comments(youtube, ids, "6Af6b_wyiwI")

    # save dict as json file
    commentFile = json.dumps(commentDict)
    f = open("dict.json","w")
    f.write(commentFile)
    f.close()



if __name__ == "__main__":
    main()