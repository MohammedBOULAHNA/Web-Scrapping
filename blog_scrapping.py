from bs4 import BeautifulSoup # import BeautifulSoup
import requests # import requests
import json # import json for data storing


# create request to archive 

blog_archive_url = 'https://enlear.academy/archive/2022/01'
response = requests.get(blog_archive_url)

# parse the response using HTML parser on 
parsedHtml = BeautifulSoup(response.text, 'html.parser')

#the stories can be queried by performing a DOM operation to fetch all the div elements that have the class list streamItem streamItem--postPreview js-streamItem

stories = parsedHtml.find_all('div', class_='streamItemstreamItem--postPreviewjs-streamItem')

# we can iterate over each story in the stories array and obtain critical meta information such as article title and subtitle, number of claps, reading time, and URL.

formatted_stories = []

for story in stories:
    # Get the title of the story
    story_title = story.find('h3').text if story.find('h3') else'N/A'# get the subtitle of the story
    story_subtitle = story.find('h4').text if story.find('h4') else'N/A'

    # Get the number of claps
    clap_button = story.find('button', class_='button button--chromeless u-baseColor--buttonNormal js-multirecommendCountButton u-disablePointerEvents')
   
    claps = clap_button.text
    
    # Gget reference to the card header containing author info
    author_header = story.find('div', class_='postMetaInline u-floatLeft u-sm-maxWidthFullWidth')
    # Access the reading time span element andget its title attribute

    reading_time = author_header.find('span', class_='readingTime')['title']

      # Get read more ref
    read_more_ref = story.find('a', class_='button button--smaller button--chromeless u-baseColor--buttonNormal')
    url = read_more_ref['href'] if read_more_ref else'N/A'

    # Add an object to formatted_stories
    formatted_stories.append({
        'title': story_title,
        'subtitle': story_subtitle,
        'claps': claps,
        'reading_time': reading_time,
        'url': url
    })

# the array is written into a JSON file using the file module of Python, as shown below.
file = open('stories.json', 'w')
file.write(json.dumps(formatted_stories))