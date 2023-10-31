# AWS-Event-Driven-Project
A simple project demonstrating the concept of Event Driven Architecture

OUTLINE:

To demonstate event driven architecture, I have a set of csv files, structured to represent housing data on each row.

The csv files will have a destination, the first S3 bucket. After which, a pre-configured trigger, will launch a lambda function, written in python, to process each csv file and send batches of rows(10) to an SQS queue.

A separate S3 bucket was used to store the lambda function.
