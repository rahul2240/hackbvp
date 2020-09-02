if [ ! -d "logs" ]
then
    mkdir -p -- "logs"
fi

if [ ! -d "videos_downloaded" ]
then 
    mkdir -p -- "videos_downloaded"
fi
exec /home/ubuntu/video-analysis/env/bin/gunicorn run:app -b 0.0.0.0:9007 -t 30  --capture-output --log-level info --access-logformat  "'%(t)s' '%(h)s', '%({X-Request-Id}i)s', ['%(s)s'], '%(m)s', '%(U)s', '%(L)s's" --access-logfile ./logs/access.log --error-logfile ./logs/error.log
