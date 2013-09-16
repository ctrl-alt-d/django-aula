#!/bin/bash
git add .
git commit -m "$1"
git push
../origen/2head
cd ../cendrassos
git add .
git commit -m "$1"
git push ghap master
