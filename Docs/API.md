# AI Service API

### Talk to an AI agent

#### Description

- The GameService sends the AI service a chat message from an online player whose intended recipient is an AI agent / offline player. The AI service retrieves relevant memories to construct a prompt that it sends to the OpenAI API. The AI serviece sends the GameService the response and the GameService adds the chat response to the chat table in the back-end database and sends along the response to the user.

#### Request

- `POST /api/agents/prompt`

  ```json
  {
    "senderId": "00000000-0000-0000-0000-000000000000",
    "recipientId": "00000000-0000-0000-0000-000000000000",
    "isRecipientUser": false,
    "conversationId": "00000000-0000-0000-0000-000000000000",
    "content": "Test message",
    "streamResponse": false
  }
  ```

#### Response

- `200 OK`

  ```
    "string"
  ```

### Prompt an AI agent to ask a question

#### Description

- The GameService sends the AI service a request from an online player whose intended recipient is an AI agent / offline player. The AI service retrieves relevant memories to construct a prompt that it sends to the OpenAI API. The AI serviece sends the GameService the response and the GameService adds the chat response to the chat table in the back-end database and sends along the response to the user.

#### Request

- `POST /api/agents/question`

  ```json
  {
    "senderId": "00000000-0000-0000-0000-000000000000",
    "recipientId": "00000000-0000-0000-0000-000000000000",
    "conversationId": "00000000-0000-0000-0000-000000000000",
    "streamResponse": false
  }
  ```

#### Response

- `200 OK`

  ```
    "string"
  ```

### Notify AI service that conversation ended

#### Description 

- On the end of any conversation taking place in the game, notify the AI service. This will allow the AI service to generate summaries of the conversation which can be stored in the vector database collections for both of the actors involved in the conversation.

#### Request

- `POST /api/agents/endConversation`

  ```json
  {
    "conversationID": "00000000-0000-0000-0000-000000000000",
    "participants": [
      "00000000-0000-0000-0000-000000000000",
      "00000000-0000-0000-0000-000000000000"
    ]
  }
  ```

#### Response

- `200 OK`


### Generate a summary for an AI persona

#### Description

- The GameService receives the question responses about a new user or a new AI Agent. It then sends those responses along to the AI Service which passes it to GPT to generate a summary of the user / agent. The AI service then returns this summary to the Game Service.

#### Request

- `POST /api/agents/generatePersona`
  ```json
  {
    "characterId": "00000000-0000-0000-0000-000000000000",
    "questions": [
      "question 1",
      "question 2",
      "question 3"
    ],
    "responses": [
      ["response to q1", "response to q1", ],
      ["response to q2", "response to q2", ],
      ["response to q3", "response to q3", ]
    ]
  }
  ```

#### Response

- `200 OK`
  ```json
  {
    "summary": "Test summary"
  }
  ```

### Generate an agent avatar

#### Description

- AI service uses generative AI to create a avatar for the agent to be displayed in game.

#### Request

- `POST /api/agents/generateAvatar`

  ```json
  {
    "appearanceDescription": "Test description"
  }
  ```

#### Response

- `200 OK`
  ```json
  {
    "avatarURL": "https://www.test.com/test_thumbnail.png",
    "headshotURL": "https://www.test.com/test_thumbnail.png"
  }
  ```

### Generate a world thumbnail

#### Description

- AI service uses generative AI to create a thumbnail for a world to be displayed on the front end.

#### Request

- `POST /api/thumbnails`

  ```json
  {
    "worldId": "00000000-0000-0000-0000-000000000000",
    "creatorId": "00000000-0000-0000-0000-000000000000",
    "description": "Test description"
  }
  ```

#### Response

- `200 OK`
  ```json
  {
    "thumbnailURL": "https://www.test.com/test_thumbnail.png"
  }
  ```
