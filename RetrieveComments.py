import os
import csv
import code
import os.path

import google_auth_oauthlib.flow
import googleapiclient.discovery
from googleapiclient.errors import HttpError

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# function that gets all comments for videos in videoId Array and saves them in a dict
def get_comments(youtube):

    # values is returned in order to check if there is still enough quota
    quotaAvailable = True

    ##### Arrays to store data #####
    comments = []
    visited = []
    commentDisabled = []
    notAvailable = []

    # load all videos to visitinto memory
    try:
        with open('videos.txt', 'r') as file:
            videoIds = file.read().split(',')
    except:
        print("No valid file with video Ids available")
        return


    # check if there exists an visited file
    if os.path.isfile('videos_visited.txt'):
        with open('videos_visited.txt', 'r') as file:
            alreadyVisited = file.read().split(',')
            # delete already visited out of to id array
            videoIds = [i for i in videoIds if i not in alreadyVisited]

    savegame = []
    if os.path.isfile('savegame.txt'):
        with open("savegame.txt", "r"):
            savegame = file.read().split(',')

    # iterate through all videos and retrieve comments
    for video in videoIds:
        if quotaAvailable:


            #check if some comments for current video were already scraped
            if not savegame or savegame[0] is not video:

                # request for first page ordered by relevance
                request = youtube.commentThreads().list(
                    part="snippet",
                    maxResults=100,
                    videoId=video,
                    order="relevance"
                )

                try:
                    response = request.execute()

                except HttpError as err:
                    if err.resp.status == 403:
                        # if error status is 403, video has comments disabled
                        commentDisabled.append(video)
                        #save video id to visited array
                        visited.append(video)

                        print(err)
                        continue

                    if err.resp.status == 404:
                        # if error status is 404, video is not available
                        notAvailable.append(video)
                        visited.append(video)

                        print(err)
                        continue
                    else:
                        quotaAvailable = False
                        print(err)

                # append comments to list
                for comment in response.get('items'):
                    commentRow =[len(comments)+1, video, comment.get('snippet').get('topLevelComment').get('snippet').get('textOriginal'), comment.get('snippet').get('topLevelComment').get('snippet').get('publishedAt')]
                    comments.append(commentRow)


                nextPageToken = response.get('nextPageToken')

            else:
                # some comments for this video were already retrieved --> start retrieving here
                nextPageToken = savegame[1]


            while nextPageToken and quotaAvailable:

                request = youtube.commentThreads().list(
                    part="snippet",
                    maxResults=100,
                    pageToken=nextPageToken,
                    videoId=video,
                    order="relevance"
                )

                try:
                    response = request.execute()
                except Exception as e:
                    print(e)
                    # quota exceeded --> save nextpagetoken + video in file
                    with open("savegame.txt", "w") as file:
                        file.write(video + "," + nextPageToken)


                    quotaAvailable = False

                # append ids to list
                for comment in response.get('items'):
                    commentRow =[len(comments)+1, video, comment.get('snippet').get('topLevelComment').get('snippet').get('textOriginal'), comment.get('snippet').get('topLevelComment').get('snippet').get('publishedAt')]
                    comments.append(commentRow)

                nextPageToken = response.get('nextPageToken')

        else:
            break

    #### save all arrays to files ####
    # save comments for video to csv file
    with open('comments.csv', 'a', encoding="utf-8", newline='') as file:
        writer = csv.writer(file)
        writer.writerows(comments)

    with open('videos_visited.txt', 'a') as file:
        appendString = "," + ','.join(visited)
        file.write(appendString)

    with open('video_notAvailable.txt', 'a') as file:
        appendString = "," + ','.join(notAvailable)
        file.write(appendString)

    with open('video_noComments.txt', 'a') as file:
        appendString = "," + ','.join(commentDisabled)
        file.write(appendString)

    return




def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    api_key= 'INSERT'

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=api_key)


######## Retrieval starts here ################

### loop over every video and call get_comments

    get_comments(youtube)




if __name__ == "__main__":
    main()
