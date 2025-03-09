# import chainlit as cl

# from parcel.flows.parcel_flow import ParcelShippingFlow  # Import your CrewAI flow


# # This function simulates an automated conversation.
# async def run_auto_conversation():
#     # Kick off the CrewAI Flow to get the initial response.
#     flow = ParcelShippingFlow()
#     initial_output = flow.kickoff()
#     await cl.send_message(f"Agent: {initial_output}")

#     # Simulated conversation loop: list of follow-up user messages.
#     simulated_user_messages = [
#         "Can you confirm the shipping rate?",
#         "I would like to know the current status of my shipment.",
#         "Thanks for the update!",
#     ]

#     for user_msg in simulated_user_messages:
#         # Optionally, update the flow state with the new user message.
#         # For example, you might update the inquiry or add additional instructions.
#         flow.state.inquiry = user_msg  # This is just for demonstration.

#         # Re-run or continue the flow to simulate the agent response.
#         # In a real-world scenario, you might have different flows/tasks for follow-ups.
#         response = flow.kickoff()
#         await cl.send_message(f"User: {user_msg}")
#         await cl.send_message(f"Agent: {response}")


# @cl.on_chat_start
# async def on_chat_start():
#     await cl.send_message("Welcome to the Shipment Service Chatbot powered by CrewAI!")
#     # Automatically start the conversation.
#     await run_auto_conversation()


# # If you also want to handle manual user input in addition to auto-generated responses:
# @cl.on_message
# async def on_message(message: str):
#     try:
#         # For a manual message, you can update the flow's state based on user input
#         flow = ParcelShippingFlow()
#         flow.state.inquiry = message
#         response = flow.kickoff()
#         await cl.send_message(f"Agent: {response}")
#     except Exception as e:
#         await cl.send_message(f"An error occurred: {str(e)}")
# --==-=--==-==---==--=-=

import chainlit as cl

from parcel.flows.parcel_flow import ParcelShippingFlow  # Import your CrewAI flow


# This function initiates the conversation.
async def agent_initiate_conversation():
    # Initialize the flow
    flow = ParcelShippingFlow()

    # Warm welcome message
    welcome_message = (
        "👋 Hello! I'm your personal shipping assistant. I can help you with:\n\n"
        "📦 Getting shipping quotes\n"
        "📝 Processing shipment requests\n"
        "🔍 Tracking existing shipments\n"
        "❓ Answering any shipping-related questions\n\n"
        "What would you like assistance with today?"
    )
    await cl.Message(content=welcome_message).send()

    # Send quick action buttons
    actions = [
        cl.Action(
            name="new_shipment",
            label="📦 New Shipment",
            payload={"action": "new_shipment"},
        ),
        cl.Action(
            name="track_shipment",
            label="🔍 Track Shipment",
            payload={"action": "track_shipment"},
        ),
        cl.Action(
            name="get_quote", label="💰 Get Quote", payload={"action": "get_quote"}
        ),
        cl.Action(name="help", label="❓ Help", payload={"action": "help"}),
    ]
    await cl.Message(content="Please select an option:", actions=actions).send()


@cl.on_chat_start
async def on_chat_start():
    await cl.Message(content="🚀 Welcome to the Parcel Shipping Assistant!").send()
    await agent_initiate_conversation()


@cl.on_message
async def on_message(message: str):
    try:
        # Initialize the flow with the user's message
        flow = ParcelShippingFlow()
        flow.state.inquiry = message

        # Check if this is an action callback
        if message.startswith("/"):
            action_name = message[1:]  # Remove the leading slash

            if action_name == "new_shipment":
                await cl.Message(
                    content=(
                        "Let's help you set up a new shipment. Please provide the following details:\n\n"
                        "1. What are you shipping? (item type and description)\n"
                        "2. Package dimensions (length x width x height)\n"
                        "3. Package weight\n"
                        "4. Pickup address\n"
                        "5. Delivery address\n\n"
                        "You can provide these details one by one or all at once."
                    )
                ).send()
                return

            elif action_name == "track_shipment":
                await cl.Message(
                    content=(
                        "Please provide your tracking number, and I'll check the status for you."
                    )
                ).send()
                return

            elif action_name == "get_quote":
                await cl.Message(
                    content=(
                        "I'll help you get a shipping quote. Please provide:\n\n"
                        "1. Package dimensions\n"
                        "2. Weight\n"
                        "3. Pickup location (city/country)\n"
                        "4. Delivery location (city/country)"
                    )
                ).send()
                return

            elif action_name == "help":
                help_message = (
                    "Here's how I can help you:\n\n"
                    "📦 **New Shipment**: Create a new shipping request\n"
                    "🔍 **Track Shipment**: Check the status of your package\n"
                    "💰 **Get Quote**: Calculate shipping costs\n"
                    "❓ **Support**: Get answers to common questions\n\n"
                    "What would you like to know more about?"
                )
                await cl.Message(content=help_message).send()
                return

            elif action_name in ["new_request", "done"]:
                if action_name == "done":
                    await cl.Message(
                        content="Thank you for using our service! Have a great day! 👋"
                    ).send()
                    return
                else:
                    await agent_initiate_conversation()
                    return

        # Process regular messages based on context
        if "track" in message.lower() and any(char.isdigit() for char in message):
            # If message contains tracking number
            tracking_info = flow.track_shipment("Tracking request")
            await cl.Message(
                content=(
                    f"📍 Tracking Status: {tracking_info['status']}\n"
                    f"Location: {tracking_info['current_location']}"
                )
            ).send()

        elif any(
            word in message.lower() for word in ["quote", "cost", "price", "rate"]
        ):
            # If user is asking for a quote
            rate_info = flow.calculate_rate("Rate request")
            await cl.Message(
                content=(
                    f"💰 Estimated Shipping Cost: ${rate_info['shipping_cost']:.2f}\n"
                    f"📅 Estimated Delivery Time: {rate_info['delivery_time']} days\n\n"
                    "Would you like to proceed with this shipment?"
                )
            ).send()

        else:
            # General inquiry processing
            response = flow.kickoff()
            await cl.Message(content=response).send()

            # Proactively ask if they need anything else
            actions = [
                cl.Action(
                    name="new_request",
                    label="📦 New Request",
                    payload={"action": "new_request"},
                ),
                cl.Action(name="done", label="✅ Done", payload={"action": "done"}),
            ]
            await cl.Message(
                content="Is there anything else you need help with?", actions=actions
            ).send()

    except Exception as e:
        await cl.Message(
            content=f"I apologize, but I encountered an error: {str(e)}\n\nHow else can I assist you?"
        ).send()
