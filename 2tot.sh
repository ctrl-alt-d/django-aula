#!/bin/bash
git add .
git commit -m "$1"
git push
~/projectes/djau/original/2head
cd ../cendrassos
git add .
git commit -m "$1"
git push ghap master
