import os
import openai
import time

client = openai.OpenAI(api_key="api_key")
assistant_id = "assistant_id"
instructions = os.environ.get("RUN_INSTRUCTIONS", "")


def create_thread(content):
    messages = [
        {
            "role": "user",
            "content": content,
        }
    ]
    thread = client.beta.threads.create(messages=messages)
    return thread


def create_message(thread, content):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=content
    )


def create_run(thread):
    run = client.beta.threads.runs.create(
        thread_id=thread.id, assistant_id=assistant_id, instructions=instructions
    )
    return run


def get_message_value_list(messages):
    messages_value_list = []
    for message in messages:
        message_content = ""
        print(message)
        if message.role == 'user':
            if hasattr(message.content[0], 'annotations'):
                annotations = message.content[0].annotations
            else:
                annotations = []
            citations = []
            for index, annotation in enumerate(annotations):
                message_content = message_content.replace(
                    annotation.text, f" [{index}]"
                )

            message_content += "\n" + "\n".join(citations)
            messages_value_list.append(message_content)
    return messages_value_list


def get_message_list(thread, run):
    completed = False
    while not completed:
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        print("run.status:", run.status)
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        print("messages:", "\n".join(get_message_value_list(messages)))
        if run.status == "completed":
            completed = True
        else:
            time.sleep(5)
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    return get_message_value_list(messages)


def get_response(thread, user_input):
    create_message(thread, user_input)
    run = create_run(thread)
    return "\n".join(get_message_list(thread, run))


def main():
    print("Assistants API UI")
    thread = create_thread("Hello, how can I assist you?")

    while True:
        user_msg = input("You: ")
        if user_msg.lower() == 'exit':
            print("Exiting conversation.")
            break
        response = get_response(thread, user_msg)
        print(f"Assistant: {response}")


if __name__ == "__main__":
    main()
