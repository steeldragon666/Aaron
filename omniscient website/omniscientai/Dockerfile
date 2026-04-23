# Build stage
FROM node:20-slim AS builder
WORKDIR /app
COPY . .

# Vite embeds VITE_* env vars at build time. Must be ARG, not just ENV,
# so Cloud Build can pass a value via --build-arg / cloudbuild.yaml
# substitutions. Default is `false` — dark deploy. Override to `true`
# to route production traffic to the v2 redesign.
ARG VITE_USE_V2=false
ENV VITE_USE_V2=$VITE_USE_V2

RUN npm install -g pnpm && pnpm install && pnpm run build

# Production stage
FROM node:20-slim
WORKDIR /app
RUN npm install -g pnpm
COPY --from=builder /app/package.json /app/pnpm-lock.yaml ./
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules

ENV NODE_ENV=production
EXPOSE 8080
CMD ["pnpm", "run", "start"]
