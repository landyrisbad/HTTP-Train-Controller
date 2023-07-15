import re
from http.server import BaseHTTPRequestHandler, HTTPServer
import mimetypes
import os

class Server(BaseHTTPRequestHandler):    

    PythonServer = ""
    Views = ""

    def parse_request(self) -> bool:
        self.raw_requestline = self.rfile.readline(65537)
        if super().parse_request():
            self.requestline = self.raw_requestline
            return True
        else:
            return False
        
    def return404():
        pass

    def handle_one_request(self):
        if not self.parse_request():
            self.send_error(69, "Fuck you lol")

        request = str(self.requestline)
        views = Server.Views
        url = urls.url_to_list(urls.get_url(request))
        if "." in url[1]:
            try:
                fileData = getattr(views, url[1])
                returnType = mimetypes.MimeTypes().guess_type(url[1])[0]
                self.do_GET(fileData, returnType)
            except Exception as e:
                print(e)
                self.send_error(404, "Resource does not exist")
        else:
            returnType = "text/html"
            methods = [method_name for method_name in dir(views) if callable(getattr(views, method_name))]
            args = [request]
            postData = self.headers["Content-Length"]
            if postData != None:
                postData = self.rfile.read(int(self.headers["Content-Length"]))
                if str(postData) != "":
                    args.append(postData)
            
            for i in range(len(methods)-1, -1, -1):
                method = methods[i]
                methodResponse = None
                try:
                    methodResponse = getattr(views, method)(*args)
                except Exception as e:
                    self.return404()
                if methodResponse != None:
                    self.do_GET(methodResponse, returnType)
                    break
    
    def do_GET(self, response, content_type):
        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.end_headers()
        try:
            self.wfile.write(response.encode())
        except:
            try:
                self.wfile.write(response)
            except Exception as e:
                print(e)

    #
    # Add all files in "static" directory (i.e. css, js files) to the views class so they can be accessed by a html request
    #
    def add_static_files(views):
        import os
        for file in os.listdir("static"):
            f = open("static/" + file, "rb")
            data = f.read()
            f.close()
            setattr(views, file, data)
    
    def run(port, views):
        Server.Views = views

        Server.add_static_files(views)

        Server.PythonServer = HTTPServer(("", port), Server)
        print(Server.PythonServer.server_address)

        try:
            Server.PythonServer.serve_forever()
        except KeyboardInterrupt:
            pass

        Server.PythonServer.server_close()
        print("Server stopped.")
            
                
class urls:
    #
    # Get the url string from the whole request
    #
    def get_url(request: str):
        try:
            start = request.index(" ") + 1
        except:
            return ""
        url = ""
        for i in range(start, len(request)):
            if request[i] == " ":
                break
            url += request[i]
            
        return url

    def url_to_list(url: str):
        return url.strip().split("/")

    def list_to_url(list_url):
        url = ""
        for part in list_url:
            if part != "":
                url += "/"
                url += part
        if url == "":
            url += "/"
            
        return url

    #
    # Takes data from a POST request and turns it into a python dictionary
    #
    def formatPOSTData(data):
        returnData = {}
        currentKey = ""
        currentValue = ""
        value = False
        data = str(data)[2:-1]
        for letter in data:
            if letter == "=":
                value = True
                continue
            if letter == "&":
                returnData[currentKey] = currentValue
                currentKey = ""
                currentValue = ""
                value = False
                continue
            if value:
                currentValue += letter
            else:
                currentKey += letter
        returnData[currentKey] = currentValue
        
        print(f"POST DATA: {returnData}")
        return returnData

    def getPOSTData(request):   
        return urls.formatPOSTData(request)

    #
    # Decorator for routing urls. Checking for urls with variables in works by substituting the placeholders with the request url to see if it matches
    #
    def route(url: str):
        def decorator(func):
            def wrapper(*args):
                result = None
                var_url = True if "<" in url or ">" in url else False # check if the route contains variables 
                check_url = urls.url_to_list(url) # url for the page
                real_url = urls.url_to_list(urls.get_url(args[0])) # from the request
                if len(check_url) != len(real_url):
                    return None
                if var_url:
                    func_vars = {}
                    for i, item in enumerate(check_url):
                        search = True if "<" in item or ">" in item else False
                        if search != False: # if the item contains angle brackets indicating it is a placeholder
                            search_item = item.replace("<", "").replace(">", "")
                            search_item = search_item.split(":")
                            if search_item[0] == "int":
                                try:
                                    func_vars[search_item[1]] = int(real_url[i])
                                except: # if the value can't be converted to int 
                                    return None # then url is invalid
                            else:
                                if search_item[0] == "str":
                                    real_url[i] = real_url[i].replace("_", " ") 
                                func_vars[search_item[1]] = real_url[i]
                        
                            check_url[i] = real_url[i]
                
                    if real_url == check_url:
                        if len(args) > 1:
                            result = func(func_vars, urls.getPOSTData(args[-1]))
                        else:
                            result = func(func_vars)
                else:
                    if urls.list_to_url(real_url) == url:
                        if len(args) > 1:
                            result = func(urls.getPOSTData(args[-1]))
                        else:
                            result = func()

                return result
            return wrapper
        return decorator


class Responses:
    #
    # Render a html page by replacing variables
    #
    import re
    def render(html: str, args = {}):
        with open("static/"+html, "r") as f:
            content = f.read().split("\n")
        
        search_pattern = re.compile("\{%(.*?)\%}") # matches "{%anything%}"
        for i, line in enumerate(content):
            search = search_pattern.search(line)
            if search != None:
                search_item = search.group(1).strip().split(" ")
                
                if search_item[0] == "html-block":
                    content[i] = Responses.render(search_item[1], args)
                elif search_item[0] == "var":
                    start = search.start()
                    end = search.end()
                    replace = content[i][start:end] # the variable tag
                    content[i] = content[i].replace(replace, str(args[search_item[1]]))
                
        html = ""
        for item in content:
            item = str(item)
            html += item
        return html       
            
    #
    # Uses javascript to cheat and implement a way to redirect
    #
    redirect_html = '''<!DOCTYPE html>
    <html>
      <head>
        <meta http-equiv="refresh" content="0; url='{}'" />
      </head>
    </html>
    '''
    def redirect(url: str):
        return Responses.redirect_html.format(url)
