FROM node:22.4.1

# Use network proxy as needed
# ARG HTTP_PROXY=http://192.168.0.241:10809
# ARG HTTPS_PROXY=http://192.168.0.241:10809

WORKDIR /NexusAI/web

COPY web /NexusAI/web

RUN npm install

CMD ["npm", "run", "preview"]