// mongo-init.js
db = db.getSiblingDB('admin');
db.auth('admin', 'password');

db = db.getSiblingDB('video_agent');
db.createUser({
  user: 'video_user',
  pwd: 'video_pass',
  roles: [{ role: 'readWrite', db: 'video_agent' }]
});