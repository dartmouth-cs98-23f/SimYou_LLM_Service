# AI Service to GameService API

## Notes

## GameService to AI Service Communication

### prompt

#### Description

- The GameService sends the AI service a chat message from an online player whose intended recipient is an AI agent / offline player. The AI service retrieves relevant memories to construct a prompt that it sends to the OpenAI API. The AI serviece sends the GameService the response and the GameService adds the chat response to the chat table in the back-end database and sends along the response to the user.

#### Request

- `Prompt(chat.Id, chat.Content, chat.SenderId, chat.RecipientId, chat.conversationID, stream);`

  ```json
  {
    "prompt": "message to prompt agent with",
    "senderId": "GUID of sender",
    "recipientId": "GUID of recipient (agent you will get a response from)",
    "conversationID": "GUID of current conversation",
    "streamResponse": "true if the AI service should stream the response, false otherwise",
    "respondWithQuestion": "true if you want the AI to shake up convo by asking a question"
  }
  ```

#### Response

- `200 OK`

  ```json
  {
    "responderID": "ID of recipient who sent the message that triggered the response",
    "questyionerID": "ID of user who originally sent the message that triggered this incoming",
    "conversationID": "GUID of current conversation",
    "content": "AI-generated response"
  }
  ```

### endConversation

#### Description 

- On the end of any conversation taking place in the game, notify the AI service. This will allow the AI service to generate summaries of the conversation which can be stored in the vector database collections for both of the actors involved in the conversation.

#### Request

- `UserToUserChatNotify(chat.Id, chat.SenderId, chat.RecipientId);`

  ```json
  {
    "chatId": "GUID GameService generates",
    "senderId": "GUID of sender",
    "RecipientId": "GUID of recipient"
  }
  ```

#### Response

- `200 OK`

### GenerateSprite (*Stretch Feature*)

#### Description

- The GameService receives either a picture of the real person's face or a description of what the user wants their sprite's appearance to look like. If it's a picture, it will be sent to the AI Service to be described by GPT into words. Then the description will be sent along to DALL-E to generate a full body sprite and a headashot of the sprite, which will then be sent back to the GameService, saved by it, and sent along to the Front-End.

#### Request

- `GenerateSprite(userId, description, photo);`

  ```json
  {
    "userId": "GUID of user",

    "description": "Description of appearance",
    or:
    "photo": "URL to photo that GameService saves in back-end"
  }
  ```

#### Response

- `200 OK`
  ```json
  {
    "userId": "GUID of user",
    "sprite": "sprite file",
    "spriteHeadshot": "sprite file",
  }
  ```

### generatePersona

#### Description

- The GameService receives the question responses about a new user or a new AI Agent. It then sends those responses along to the AI Service which passes it to GPT to generate a summary of the user / agent. The AI service then returns this summary to the Game Service.

#### Request

- `GenerateCharacterSummary(characterId, responses);`
  ```json
  {
    "characterId": "GUID of user/agent",
    "questions": ["question 1", "question 2", "question 3"],
    "answers": [["response to q1", "response to q1", ] ["response to q2", "response to q2", ], ["response to q3", "response to q3", ]]
  }
  ```

#### Response

- `200 OK`
  ```json
  {
    "characterId": "GUID of user/agent",
    "generatedSummary": "summary"
  }
  ```

### generateWorldThumbnail

#### Description

- AI service uses generative AI to create a thumbnail for a world to be displayed on the front end.

#### Request

- `GenerateWorldThumbnail(worldId, description, creatorId);`

  ```json
  {
    "worldId": "GUID of World",
    "description": "string",
    "creatorId": "GUID of user"
  }
  ```

#### Response

- `200 OK`
  ```json
  {
    "worldID": "GUID of user/agent",
    "photo": "URL to photo that GameService saves in back-end"
  }
  ```
