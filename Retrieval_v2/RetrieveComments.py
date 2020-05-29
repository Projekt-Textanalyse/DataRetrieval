import os
import json
import code
import os.path

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

    try:
        response = request.execute()

    except Exception as e:
        print("EXECUTING ID REQUEST FAILED:" + e)

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
        try:
            response = request.execute()
        except Exception as e:
            print("EXECUTING REQUEST FAILED:" + e)
            break

        # append ids to list
        for comment in response.get('items'):
            ids.append(comment.get('id'))
        
        nextPageToken = response.get('nextPageToken')

    return ids

# function that gets all comments by id and saves them in a dict
def get_comments(youtube, videoId):

    # if ids were already retrieved load them into array 
    if os.path.isfile('./ids/' + videoId + '_ids.txt'):
        with open('./ids/' + videoId + '_ids.txt', 'r') as file:
            commentIds = file.read().split(',')
            # remove last elem because its empty
            commentIds.pop()

    else:
        #if no file exists, get ids and save them to file
        commentIds = get_ids(youtube, videoId)
        with open('./ids/' + videoId + '_ids.txt', 'w') as file:
            for id in commentIds:
                file.write(id + ',')


    # check if there exists an visited file
    if os.path.isfile('./visited/'+ videoId + '_visited.txt'):
        with open('./visited/' + videoId + '_visited.txt', 'r') as file:
            alreadyVisited = file.read().split(',')
            #remove last elem because its empty
            alreadyVisited.pop()
            # delete already visited out of to id array
            commentIds = [i for i in commentIds if i not in alreadyVisited] 

    # declare arrays to be filled later on
    comments = []
    idsVisited = []

    for commentId in commentIds:

        request = youtube.comments().list(
            part="snippet",
            id=commentId
        )
        
        try:
            response = request.execute()
        
        except Exception as e:
            print("EXECUTING COMMENT REQUEST FAILED:" + e)
            break
        
        try:

            comment = {
                'id' : commentId,
                'text': response.get('items')[0].get('snippet').get('textOriginal'),
                'date': response.get('items')[0].get('snippet').get('publishedAt')
            }

            comments.append(comment)
            idsVisited.append(commentId)

        except Exception as e:

            print("Appending comment failed: " + commentId + "/n" + e)
            continue
    
    # check if dict already exists
    # add new entries to file if exists   
    if os.path.isfile('./comments/' + videoId + '_comments.json'):
        with open('./comments/' + videoId + '_comments.json', 'r') as file: 
            dataObject = json.load(file)
        joinedComments = dataObject.get('comments') + comments

        commentDict = {
            "videoId": videoId,
            "comments": joinedComments
        }
        with open('./comments/' + videoId + '_comments.json', 'w') as file:
            outputObject = json.dumps(commentDict)
            file.write(outputObject)
    else:
        commentDict = {
            "videoId": videoId,
            "comments": comments
        }
        commentFile = json.dumps(commentDict)
        with open('./comments/' + videoId + '_comments.json', 'w') as file: 
            file.write(commentFile)

    # save visited ids to file
    with open('./visited/' + videoId + '_visited.txt', 'a') as file:
        for id in idsVisited:
            file.write(id +',')
    
    return






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

    commentDict = get_comments(youtube, "6Af6b_wyiwI")




if __name__ == "__main__":
    main()