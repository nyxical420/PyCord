# PyCord
A Discord Chat Only Client made in Python.

> :warning: Warning\
> PyCord will only work to Modern Consoles like Windows Terminal and other. since the Textual Library bugs out on Classic Consoles.\
> PyCord also needs Message and Members Intent to work properly.

## Setup
This is a Step by Step setup on how to get PyCord working.

### 1: Creating a Discord Bot
PyCord uses a Discord Bot to act as a User Account. to create a Discord Bot, you will need to visit the [Discord Developer Portal](https://discord.com/developers/applications) and create a **New Application** and give your Bot a Name!\
![image](https://user-images.githubusercontent.com/53323309/194804360-40ccc7b1-ed3e-41e7-8449-4f1e519ac210.png)

After that, You will click on the **Bot** menu at the Side Panel and click on **Add Bot** at the right side of your screen.
![image](https://user-images.githubusercontent.com/53323309/194804455-ce8141f4-da0f-487d-bcf3-920060009030.png)

After that, you will need to scroll down a little until you see **Privileged Gateway Intents** then enable the **Message Content Intent** and **Server Members Intent**
![image](https://user-images.githubusercontent.com/53323309/194805403-d33bd4f3-378e-42d2-b918-7824673c6980.png)
> These two intents are Required to run PyCord.

### 2: Setting up .env Bot Token Value
Now that we created a bot, we will now need it's token to start the bot.\
If you have 2 Factor Authorization in your Discord Account, you may need your [Authenticator App](https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2&hl=en&gl=US) to proceed to this next step.

To get your Discord Bot Token, simply press **Reset Token** and click on **Copy**.
> If you have 2FA in your account, you will need to enter your Authentication Code before you can get your Discord Bot's token.

Now that we have our Discord Bot's token. we will now edit our .env file that's Included on the PyCord ZIP file.\
To edit our .env file, You will need to Press `Win+R` and type in `notepad.exe` and press enter.
![image](https://user-images.githubusercontent.com/53323309/194805835-95890c6e-634a-4430-b0e0-a9c07b310d7c.png)

Now that we opened the Notepad Program, drag the .env file inside the Notepad Window and paste our Discord Bot's Token next to the `token` Value then Save.\
![image](https://user-images.githubusercontent.com/53323309/194806065-e8f5f6cb-e6ca-4202-add0-63273221ca5c.png)

### 3: Running PyCord on Windows Terminal
Now that we have everything set, we will now need to run PyCord on a Fancy Terminal so we don't run into problems while using PyCord (on a non-fancy terminal).
In this step, you will need to install [Windows Terminal](https://apps.microsoft.com/store/detail/windows-terminal/9N0DX20HK701) on the Microsoft App Store.\
![image](https://user-images.githubusercontent.com/53323309/194806617-0584c4ac-e91f-4f20-bc60-cd72ede40689.png)

After installation is done, we can Run Windows Terminal by opening the folder that contains the PyCord Executable and pressing **Open In Terminal**\
![image](https://user-images.githubusercontent.com/53323309/194806978-5ece13d9-aa8a-4311-963d-90d7584e10e5.png)

Now that we opened Windows Terminal, run `.\PyCord` inside the terminal to start PyCord!
