# United Shield Space - Desktop App <img src="/githubGraphics/logo.png" align="right" width="266" height="131" />
Monolithic Architecture based Public Cloud Storage Service for encrypted text file storage with Server side written in GoLang and Client side GUI written in Python. Client and Server communicate over gRPC Services.

## Screenshots
<img src="/githubGraphics/splash-screen.png"/>
<img src="/githubGraphics/login-screen.png"/>
<img src="/githubGraphics/sign-up-screen.png"/>
<img src="/githubGraphics/home-screen.png"/>
<img src="/githubGraphics/file-options.png"/>
<img src="/githubGraphics/server-logging.png"/>
<img src="/githubGraphics/db-user-node.png"/>
<img src="/githubGraphics/db-file-node.png"/>
<img src="/githubGraphics/firebase-file.png"/>

## Watch a Demo
[![Watch the video](https://media.giphy.com/media/XBdaS9VD83Pk63s5DM/giphy.gif)](https://youtu.be/5sNnQHXtfUA)

## Technologies Used
- Python3
- Tkinter
- GoLang
- gRPC (Protocol Buffers)
- Mongo DB
- Firebase Cloud Storage

## Features
 - Simple GUI made using Tkinter
 - User Login/Signup Functionality
 - Server side file encryption/decryption
 - Authentication of every using JWT
 - Separate JWT for file download, compiled based on Requestor

## How to use?
 - Just clone the repository
 - Run "make" in both /server and /client dirctory
 - Setup files
    - /server/.env
    - /server/firebase/secrets
    - /server/db/ussmongo.go (Check comment)
 - Start server server/main.go
 - Run client/main.py

## Important Note
This is not production ready, but can prove a very good resource to understand concepts

## Credits
 - Firebase Storage/Google Cloud Storage Official Documentation
 - Mongo DB Official Documentation
 - gRPC Official Documentation
 - Lovely Medium Articles
 - Stack Overflow
 - University Professors

## About the developer (ME)
Checkout my website: [Karan Balani](https://krnblni.github.io)
Connect with me on LinkedIn ❤️

## License
GPLv3 (General Public License 3.0) 

GPL © [Karan Balani](https://krnblni.github.io)
