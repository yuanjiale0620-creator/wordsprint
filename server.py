#!/usr/bin/env python3
import hashlib, json, os, secrets, sqlite3
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

DB='quiz.sqlite3'; sessions={}
TEACHER_USERNAME='Julia Yuan'
TEACHER_PASSWORD_HASH=os.environ.get('TEACHER_PASSWORD_HASH','')
DEFAULT_UNITS=[{"id":1,"title":"Unit 1 · Feelings & People","subtitle":"Describe people with clear, useful words.","words":[]}]
def db():
 c=sqlite3.connect(DB); c.execute('create table if not exists attempts(id integer primary key,name text,unit text,score int,total int,seconds int,attempt int,passed int,submitted_at text default current_timestamp)'); c.execute('create table if not exists units(id integer primary key,title text,subtitle text,words text)'); c.commit(); return c
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw): super().__init__(*a,directory='.',**kw)
 def send_json(self,obj,status=200):
  b=json.dumps(obj,ensure_ascii=False).encode(); self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Access-Control-Allow-Origin','*'); self.send_header('Access-Control-Allow-Headers','Content-Type, Authorization'); self.send_header('Access-Control-Allow-Methods','GET, POST, OPTIONS'); self.send_header('Content-Length',str(len(b))); self.end_headers(); self.wfile.write(b)
 def do_OPTIONS(self):
  self.send_response(204); self.send_header('Access-Control-Allow-Origin','*'); self.send_header('Access-Control-Allow-Headers','Content-Type, Authorization'); self.send_header('Access-Control-Allow-Methods','GET, POST, OPTIONS'); self.end_headers()
 def body(self):
  n=int(self.headers.get('Content-Length',0)); return json.loads(self.rfile.read(n) or '{}')
 def do_POST(self):
  path=urlparse(self.path).path; data=self.body(); con=db()
  if path=='/api/attempts':
   con.execute('insert into attempts(name,unit,score,total,seconds,attempt,passed) values(?,?,?,?,?,?,?)',(data.get('name',''),data.get('unit',''),data.get('score',0),data.get('total',100),data.get('seconds',0),data.get('attempt',1),int(data.get('passed',False)))); con.commit(); con.close(); return self.send_json({'ok':True})
  if path=='/api/units':
   if not self.authorized(): return self.send_json({'error':'Teacher login required'},401)
   con.execute('insert or replace into units(id,title,subtitle,words) values(?,?,?,?)',(data['id'],data['title'],data.get('subtitle',''),json.dumps(data.get('words',[]),ensure_ascii=False))); con.commit(); con.close(); return self.send_json(data)
  if path=='/api/login':
   supplied=hashlib.sha256(str(data.get('password','')).encode()).hexdigest()
   if data.get('username')==TEACHER_USERNAME and secrets.compare_digest(supplied,TEACHER_PASSWORD_HASH): token=secrets.token_urlsafe(32); sessions[token]=True; return self.send_json({'ok':True,'token':token})
   return self.send_json({'error':'用户名或密码错误'},401)
  self.send_error(404)
 def do_GET(self):
  path=urlparse(self.path).path; con=db()
  if path=='/api/attempts':
   if not self.authorized(): return self.send_json({'error':'Teacher login required'},401)
   rows=[dict(zip(['id','name','unit','score','total','seconds','attempt','passed','submitted_at'],r)) for r in con.execute('select id,name,unit,score,total,seconds,attempt,passed,submitted_at from attempts order by id desc')]; con.close(); return self.send_json(rows)
  if path=='/api/units':
   rows=[{'id':r[0],'title':r[1],'subtitle':r[2],'words':json.loads(r[3])} for r in con.execute('select id,title,subtitle,words from units')]; con.close(); return self.send_json(rows)
  con.close(); return super().do_GET()
 def authorized(self):
  header=self.headers.get('Authorization','')
  return header.startswith('Bearer ') and sessions.get(header[7:]) is True
if __name__=='__main__':
 db().close(); port=int(os.environ.get('PORT','8000')); print(f'WordSprint: http://0.0.0.0:{port}'); ThreadingHTTPServer(('0.0.0.0',port),H).serve_forever()
