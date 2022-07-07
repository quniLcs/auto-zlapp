# Auto-Zlapp

## Attention

The original code is from https://github.com/FDUCSLG/pafd-automated, while the code in this repo has been optimized. It should be emphasized that the author created this repo mainly to learn web program at first; though the desire to win the competition with her girlfriend's boyfriend may also be a factor as time went by, the function of auto zlapp is always the least important reason.

## Programming Requirements

- `time`: to get today's date;
- `os`: to get environment variables and manage files;
- `string`: to get strings;
- `re`：to match strings;
- `json`: to load strings as dictionaries;
- `getpass`: to get password from keyboard input;
- `easyocr`: to read captcha;
- `io`: to convert the type of image data;
- `numpy`: the same as above;
- `PIL`: to enhance image;

- `requests`: to manage the webpage.

## User Installation

As is described in 'Attention' part, users had better follow the original [instruction](https://github.com/FDUCSLG/pafd-automated), or there's a simple summary here:

1. Fork this repo;

2. In one's own repo, follow `Setting`, `Secrets`, `Actions`;

3. Create 2 new secrets, which will be keep confidential by GitHub;

   | Number | Name             | Value                    |
   | ------ | ---------------- | ------------------------ |
   | 1      | `FUDAN_ID`       | One's Fudan UIS ID       |
   | 2      | `FUDAN_PASSWORD` | One's Fudan UIS Password |

4. Done! GitHub Action will help one to zlapp according to history information 10 a.m. every day.
