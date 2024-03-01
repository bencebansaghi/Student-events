# Student-events
A telegram chatbot which displays the information about events found on instagram pages.

## Table of Contents
- Getting Started
  - Prerequisites
  - Installation
- Usage
- Contributing
- License
- Contact
- Acknowledgments

## Getting started 

These instructions will get you a copy of the project up and running on your local machine for development and execution purposes.

### Prerequisites

Before you begin, ensure you have met the following requirements:
- You have installed the latest version of python and pip

### Installation

1. Clone the repository:
git clone https://github.com/bencebansaghi/Student-events
2. Navigate to the project directory:
cd Student-events
3. Install the required packages:
pip install -r requirements.txt


## Usage

To use Student-Events, follow these steps:

1. Set up your `.env` file in project directory. Required parameters: 
- BOT_TOKEN - Instructions for getting the token can be found at https://core.telegram.org/bots/tutorial
- OPENAI_API_KEY - Requires OpenAI API access
- INSTA_USERNAME
- INSTA_PASSWORD
- INSTAGRAM_PAGES
- CSV_FILE_PATH
- ADMIN_PASSWORD (not mandatory, only for manual adjustments)
2. Run the bot:
