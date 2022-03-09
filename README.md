# dreambox-bot
One of my first python projects.

Don't judge my code too hard, im just starting out.

First, make a config.json file with the contents of:
{"email": "your email", "password": "your password", "clever": "only applicable if you use clever to sign in"}

If you sign into dreambox on the play.dreambox.com site, you would change the email and password things with the username and pass to your dreambox account. If you use clever to sign in, you would replace them with your corresponding clever username and password (likely just google account stuff)

The clever part only applies to people who are using to clever to sign in, (if you are using dreambox to sign in, you're ready to use the script) For the clever users, you would replace that part with the link that shortly pops up after you click the dreambox icon. It would look something like this:

https://clever.com/oauth/authorize?channel=clever-portal&client_id=blahblahblah&confirmed=true&district_id=blahblahblah&redirect_uri=https%3A%2F%2Fplay.dreambox.com%2Flogin%2Fclever_oauth&response_type=code

and then, you're pretty much done. just install all of the modules in requirements.txt and run the script IN CMD (or whatever you want to call it)

Also, you cant use most vpns with this because then you sometimes get captchas and i dont want to add captcha support

# Don't abuse this, I don't want to be involved in any way with how you use it.
