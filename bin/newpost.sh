#!/usr/bin/env bash

# generate a new post with date and everything in "/_posts"
# we do this by creating a file called 
#   YYYY-MM-DD-<title>.md
# where all spaces in <title> are replaced with "-".
# and filling it with the following content:
# ```
# ---
# layout: post
# title: <title>
# author: Luca Leon Happel
# date: YYYY-MM-DD Weekday HH:MM
# category: posts
# draft: false
# ---
# ```

# Get the current date and time
current_date=$(date +%Y-%m-%d)
current_weekday=$(date +%A)
current_time=$(date +%H:%M)

# Read the title from user input
read -p "Enter the title of the post: " title

# Replace spaces in the title with dashes
formatted_title=$(echo "$title" | tr ' ' '-')

# Create the filename with the formatted title
filename="$current_date-$formatted_title.md"

# Create the file in "/_posts" directory
touch "/_posts/$filename"

# Add the content to the file
cat << EOF > "/_posts/$filename"
---
layout: post
title: $title
author: $AUTHOR
date: $current_date $current_weekday $current_time
category: posts
draft: false
---
EOF

echo "New post created: /_posts/$filename"
