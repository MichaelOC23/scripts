from notion_client import Client
import json
import os

# Initialize the Notion client
notion = Client(auth=os.environ["NOTION_API_KEY"])
blocks_list = []

parent_page_id = "96edc3216e7248d583bfd0772ba045f4"

# Heading
blocks_list.append({
    "object": "block",
    "type": "heading_1",
    "heading_1": {
        "rich_text": [
            {
                "type": "text",
                "text": {
                    "content": "My Header",
                    "link": {"url": "https://www.example.com"}
                }
            }
        ]
    }
})

# Text with Link
blocks_list.append({
    "object": "block",
    "type": "paragraph",
    "paragraph": {
        "rich_text": [
            {
                "type": "text",
                "text": {
                    "content": "This is some text.",
                    "link": {"url": "https://www.example.com"}
                }
            }
        ]
    }
})

# Multi-Block Text with Formatting
blocks_list.append({
    "object": "block",
    "type": "paragraph",
    "paragraph": {
        "rich_text": [
            {
                "type": "text",
                "text": {"content": "Here is more text", "link": None}
            },
            {
                "type": "text",
                "text": {"content": "bolded", "link": None},
                "annotations": {
                    "bold": True,
                    "italic": False,
                    "strikethrough": False,
                    "underline": False,
                    "code": False,
                    "color": "default"
                }
            },
            {
                "type": "text",
                "text": {"content": ".", "link": None}
            }
        ]
    }
})

# Column List
blocks_list.append({
    "object": "block",
    "type": "column_list",
    "column_list": {},
    "children": [
        {
            "object": "block",
            "type": "column",
            "column": {},
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "This is the first column."
                                }
                            }
                        ]
                    }
                }
            ]
        },
        {
            "object": "block",
            "type": "column",
            "column": {},
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "This is the second column."
                                }
                            }
                        ]
                    }
                }
            ]
        }
    ]
})


new_page = {
    "parent": {"page_id": parent_page_id},
    "properties": {
        "title": {
            "title": [
                {
                    "type": "text",
                    "text": {"content": "Page with Rich Text and URL"}
                }
            ]
        }
    },
    "children": blocks_list
}

try:
    response = notion.pages.create(**new_page)
    print("Page created successfully:", json.dumps(response, indent=2))
except Exception as e:
    # Detailed logging of Error
    print("Error creating page:", e)
    if hasattr(e, 'response') and hasattr(e.response, 'json'):
        data = e.response.json()
        print("Detailed Error Message:", json.dumps(data, indent=2))
