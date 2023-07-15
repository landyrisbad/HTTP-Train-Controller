from server import Server, Responses, urls

class Views:  
    @urls.route("/")
    def index():
        return Responses.render("index.html")

Server.run(80, Views)