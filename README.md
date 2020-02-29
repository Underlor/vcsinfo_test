VCS INFO
========
This script collects data about user repositories from working directories. 

Install
-----
`pip install git+https://github.com/Underlor/vcsinfo_test#egg=vcs-info-test`

Usage
-----
`vcsinfo --users-file users.json` 

Or if you want to change project path on server 
`vcsinfo --users-file users.json --project-path ~/bw` 


Example of users file
-----
```
[
  {
    "hostname": "Server1",
    "user": "user1"
  },
  {
    "hostname": "Server1",
    "user": "user2"
  },
  {
    "hostname": "Server2",
    "user": "user3",
    "key_path": "full_path_to_key"
  }
]
```
