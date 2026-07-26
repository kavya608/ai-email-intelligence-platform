def generate_reply(
    subject,
    body,
    category,
    deadline,
    action_items,
    tone="professional"
):

    if tone == "friendly":
        return (
            f'Hi,\n\n'
            f'Thank you for your email regarding "{subject}".\n\n'
            f"I'll look into it and get back to you soon.\n\n"
            f"Best,\n"
            f"AI Email Intelligence Platform"
        )
    
    elif tone == "formal":
        return (
            f'Dear Sir/Madam,\n\n'
            f'Thank you for your email regarding "{subject}".\n\n'
            f'Your request has been received and will be processed shortly.\n\n'
            f'Kind Regards,\n'
            f'AI Email Intelligence Platform'
        )

    else:
        reply = f"Hi,\n\n"

        reply += f'Thank you for your email regarding "{subject}".\n\n'

        if category == "Action Needed":
            reply += "I have noted the requested action.\n"

        elif category == "Meeting":
            reply += "I have noted the meeting invitation.\n"

        elif category == "Urgent":
            reply += "I understand that this is an urgent request and will prioritize it.\n"

        if action_items:
            if isinstance(action_items, list):
                action_text = "\n".join(action_items)
            else:
                action_text = action_items

            reply += f"\nI will take care of the following:\n{action_text}\n"

        if deadline:
            reply += f"\nI will ensure this is completed before {deadline.strftime('%d %B %Y at %I:%M %p')}."

        if tone == "friendly":
            reply += "\n\nBest,\nAI Email Intelligence Platform"

        elif tone == "formal":
            reply += "\n\nKind Regards,\nAI Email Intelligence Platform"

        else:
            reply += "\n\nRegards,\nAI Email Intelligence Platform"

        return reply

        
       
