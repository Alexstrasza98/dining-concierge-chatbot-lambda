# Overview

This is a serverless, microservice-driven web application using AWS (Amazon Web Service). Specifically, it is a Dining Concierge chatbot, that sends customer restaurant suggestions given a set of preferences that he or she provides the chatbot with through conversation.



We gather all of our code here. **Note that the code here cannot be run directly** because we use AWS to delopy this application. Almost half of the work is to create and configure AWS components. The used AWSs are listed as followings:

- **S3** (deploy front-end stuff)
- **API Gateway** with swagger (RESTful APIs)
- **Lambda** function in AWS to handle request from front-end
- **Lex** enables chatbot to chat and collect customer's intent (size of pizza, topping etc.)
  - Lex a service for building conversational interfaces into any application using voice and text.
- **SQS** stores request and we have another lambda function to pull requests from the queue periodically.
  - Simple Queue Service (SQS) is a fully managed message queuing service that enables you to decouple and scale microservices, distributed systems, and serverless applications
- **dynamoDB**: a noSQL database to store resturants data
  - we pull resturants data from yelp everyday
- **ElasticSearchService** for quick search of restaurants



# Architecture View

![image](https://user-images.githubusercontent.com/20517842/75211108-f9502200-5750-11ea-87d9-63cc59b1ec66.png)
