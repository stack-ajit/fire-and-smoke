import os
import csv
import argparse
from typing import List, Dict, Any
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file
load_dotenv(find_dotenv())

# Set up your API key as an environment variable or replace this string
API_KEY = os.environ.get("YOUTUBE_API_KEY", "YOUR_YOUTUBE_API_KEY_HERE")

def search_youtube_videos(
    youtube, 
    query: str, 
    max_results: int = 50, 
    video_license: str = "creativeCommon",
    video_duration: str = "any",
    order: str = "relevance"
) -> List[Dict[str, Any]]:
    """
    Search for YouTube videos matching the criteria.
    """
    print(f"Searching for '{query}'...")
    videos = []
    next_page_token = None
    
    while len(videos) < max_results:
        try:
            # Calculate how many results to fetch in this page
            fetch_count = min(50, max_results - len(videos))
            
            # Execute the search request
            search_request = youtube.search().list(
                part="id,snippet",
                q=query,
                type="video",
                videoDefinition="high",
                videoLicense=video_license,
                videoDuration=video_duration,
                order=order,
                maxResults=fetch_count,
                pageToken=next_page_token
            )
            search_response = search_request.execute()
            
            # Extract video IDs from search results
            video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]
            
            if not video_ids:
                break
                
            # Fetch detailed information for these videos (for duration, license, etc.)
            videos_request = youtube.videos().list(
                part="id,snippet,contentDetails,status",
                id=",".join(video_ids)
            )
            videos_response = videos_request.execute()
            
            # Process the detailed video responses
            for item in videos_response.get("items", []):
                videos.append({
                    "video_id": item["id"],
                    "title": item["snippet"]["title"],
                    "channel": item["snippet"]["channelTitle"],
                    "url": f"https://www.youtube.com/watch?v={item['id']}",
                    "duration": item["contentDetails"]["duration"],
                    "published_date": item["snippet"]["publishedAt"],
                    "license": item["status"]["license"],
                    "search_query": query
                })
            
            # Check if there are more pages
            next_page_token = search_response.get("nextPageToken")
            if not next_page_token:
                break
                
        except HttpError as e:
            print(f"An HTTP error {e.resp.status} occurred: {e.content}")
            break
            
    return videos

def export_to_csv(videos: List[Dict[str, Any]], filename: str):
    """
    Export video data to a CSV file.
    """
    if not videos:
        print("No videos found to export.")
        return
        
    print(f"Exporting {len(videos)} videos to {filename}...")
    
    fieldnames = [
        "video_id", "title", "channel", "url", 
        "duration", "published_date", "license", "search_query"
    ]
    
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for video in videos:
            writer.writerow(video)
            
    print("Export complete.")

def main():
    parser = argparse.ArgumentParser(description="Fetch YouTube video metadata into a CSV.")
    parser.add_argument("--queries", nargs="+", required=True, 
                        help="List of search queries (e.g., 'fire and smoke' 'wildfire')")
    parser.add_argument("--output", type=str, default="youtube_fire_smoke_videos.csv", 
                        help="Output CSV filename")
    parser.add_argument("--max-results", type=int, default=50, 
                        help="Maximum number of results per query")
    parser.add_argument("--license", type=str, default="creativeCommon", 
                        choices=["any", "creativeCommon", "youtube"],
                        help="License type (default: creativeCommon)")
    parser.add_argument("--duration", type=str, default="any", 
                        choices=["any", "long", "medium", "short"],
                        help="Video duration (default: any)")
    
    args = parser.parse_args()
    
    if API_KEY == "YOUR_YOUTUBE_API_KEY_HERE":
        print("WARNING: Using default API key placeholder. The script will likely fail.")
        print("Please set the YOUTUBE_API_KEY environment variable or edit the API_KEY variable in the script.")
        
    try:
        youtube = build("youtube", "v3", developerKey=API_KEY)
        
        all_videos = []
        for query in args.queries:
            videos = search_youtube_videos(
                youtube=youtube,
                query=query,
                max_results=args.max_results,
                video_license=args.license,
                video_duration=args.duration
            )
            all_videos.extend(videos)
            
        export_to_csv(all_videos, args.output)
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
