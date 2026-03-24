---
title: "This Repository Contains the Blog Structure Only"
date: "2026-03-17"
slug: "this-repository-contains-the-blog-structure-only"
description: "This repository is the companion deployment repo for the blog migration roadmap and only exposes the Hugo structure used to self-host the site."
tags: ["hugo", "kubernetes", "gitops", "platform-engineering"]
---

If you came here after reading my post about [why I'm self-hosting the blog like a bank website](https://andreivasiliu.com/from-hashnode-to-kubernetes-why-im-self-hosting-my-blog-like-a-bank-website/), this repository is the practical companion to that roadmap.

In that article, I explain the objective: use a real public-facing application to show how platform engineering pieces fit together end to end, from source code to production URL. The blog is the workload. This repository is the stripped-down implementation surface.

That is why this repository does not mirror the full published archive.

Keeping every article here would add noise to the part I actually want to document in public: how the site is structured, packaged, versioned, and deployed. So this repo focuses on the mechanics behind the blog rather than the entire writing catalog.

What you should expect to find here:

- The Hugo site structure and content layout
- Theme integration and custom layout overrides
- The page bundle shape used for posts
- The deployment-oriented pieces that support containerization and Kubernetes delivery

What you should not expect to find here:

- The complete blog archive
- Every published article from the production site
- A one-to-one copy of [andreivasiliu.com](https://andreivasiliu.com)

If your goal is to read the actual articles, use the production site instead:

- [Main blog](https://andreivasiliu.com)
- [Archive](https://andreivasiliu.com/archive/)
- [Roadmap post](https://andreivasiliu.com/from-hashnode-to-kubernetes-why-im-self-hosting-my-blog-like-a-bank-website/)

If your goal is to understand the delivery side of the platform, this repository is the relevant piece. It exists to make the roadmap post concrete.

- You can inspect how the site is organized.
- You can follow how the blog is prepared for containerization.
- You can review the structure that will be used for CI/CD, Helm, and GitOps-driven Kubernetes deployment.

So the short version is this: the main blog explains the why and the sequence of work, while this repository exposes the how for the deployment side.

If you landed here from GitHub, that is the intended scope of this repository.