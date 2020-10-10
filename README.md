# BritishCouncil.am IELTS exam days parser and informer

This package is designed to be used inside google cloud functions. These are the steps that it will do.
- fetch and parse the available dates of IELTS Academic exams
- save the dates in the datastore, compare with the old values and if new dates found, send message with telegram bot

It's controlling the permissions of telegram bot with the registered usernames in the google datastore. This is just a tool to be informed if some new dates are available for the IELTS Academic exam :) 
