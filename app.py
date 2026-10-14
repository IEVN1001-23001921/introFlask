from flask import Flask, render_template

app=Flask(__name__)

@app.route('/')
def index():
    titulo="PWA"
    lista=["Pedro", "Luis", "Armando"]
    return render_template("index.html",titulo=titulo,lista=lista)


@app.route("/hola")
def func():
    return "Holaaaa"

@app.route("/user/<string:user>")
def user(user):
    return "holis: " + user


@app.route("/numero/<int:n>")
def numero(n):
    return "Numero: {}".format(n)

@app.route("/user/<int:id>/<string:username>")
def username(id, username):
    return "ID: {} nombre: {}".format(id, username) 

@app.route("/suma/<float:n1>/<float:n2>")
def suma(n1, n2):
    return "la suma es : {}".format(n1+n2)





if __name__=="__main__":
    app.run(debug=True)