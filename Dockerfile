# syntax=docker/dockerfile:1

ARG NODE_VERSION=16.20.2
FROM node:${NODE_VERSION}

# Working directory inside container
WORKDIR /usr/src/app

# Copy server.js to write CSV files from POST
COPY server.js ./

# Copy Vue app package files
# COPY MoTR/run_motr_in_magpie/attachment/package*.json ./

COPY MoTR/run_motr_in_magpie/attachment ./
# Install CLI and dependencies
RUN npm install -g @vue/cli
RUN npm install

# Copy rest of the Vue project

# Build the frontend
RUN npm run build
RUN ls -l dist/

# Install file servers
RUN npm install -g serve
# Install server dependencies (like express, cors)
RUN npm install express cors

# Expose frontend and backend ports
EXPOSE 3000 3001
RUN mkdir -p outputs

# Run both frontend and backend together
CMD ["sh", "-c", "npx serve -s dist -l 3000 & node server.js"]
