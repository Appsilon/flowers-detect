# Flower genus detection app
Model and interface for detecting flower genus.

app based on https://github.com/simonw/cougar-or-not (and its incarnations in https://github.com/Appsilon/defect-detection, and https://github.com/Appsilon/car-damage)


## How to run

```
docker build . -t flowers
docker run -p 80:8008  flowers
# or with mounted directory for faster development:
docker run -p 80:8008 -v $(pwd)/app:/app flowers
```

Now open http://localhost
