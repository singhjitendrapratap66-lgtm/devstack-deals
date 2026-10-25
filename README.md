# DevStack & AI Deals Aggregator (Automated & Zero-Cost)

<a href="https://www.digitalocean.com/?refcode=b8677cf8f4c9&utm_campaign=Referral_Invite&utm_medium=Referral_Program&utm_source=badge"><img src="https://web-platforms.sfo2.cdn.digitaloceanspaces.com/WWW/Badge%202.svg" alt="DigitalOcean Referral Badge" /></a>

An automated, self-updating deals, cloud-credits, and AI software aggregator designed to run 100% on free-tier infrastructure (GitHub Actions + GitHub Pages).

---

## 🚀 How It Works (100% Free Architecture)

1. **Scheduled Ingestion (`aggregator.py`)**:
   - Runs automatically on GitHub Actions every 6 hours via cron (`0 */6 * * *`).
   - Fetches dynamic feeds from developer communities, product launches, and curated feeds.
   - Injects referral and affiliate parameters to monetize outbound traffic.
   - Deduplicates items and stores clean JSON in `data/deals.json`.

2. **Static Site Compiler (`build.py`)**:
   - Compiles structured deals into a single responsive HTML web application (`dist/index.html`).
   - Features client-side real-time instant search, category filtering, and responsive dark-mode styling.
   - Compliant with FTC affiliate disclosure guidelines.

3. **Zero-Cost Deployment (`.github/workflows/update.yml`)**:
   - GitHub Actions automates execution and deploys directly to **GitHub Pages** with free global CDN and SSL.

---

## 💰 Monetization Channels Setup

### 1. Affiliate Programs (Pay-Per-Sale / Free Signups)
Replace the default links in [`config.json`](file:///C:/Users/VHPL-1033/.gemini/antigravity/scratch/dealpulse-aggregator/config.json) with your own affiliate IDs:
* **DigitalOcean Referral**: Grants \$200 credits to users, awards \$25 cash per paying signup.
* **Impact Radius / AppSumo**: Up to 25% commission on software lifetime deals.
* **PartnerStack / Rewardful**: Recurring SaaS commissions (e.g., Supabase, Make, Notion affiliates).
* **Amazon Associates**: Optional hardware/books tag.

### 2. Display Ads (Optional)
When you reach steady daily traffic, insert your script snippet into [`templates/index.html`](file:///C:/Users/VHPL-1033/.gemini/antigravity/scratch/dealpulse-aggregator/templates/index.html):
* **Carbon Ads / EthicalAds**: Tailored for developer tools and privacy-friendly.
* **Google AdSense**: Standard display ad network.

---

## 🛠 Local Development & Testing

Run locally on any machine with Python 3:

```bash
# 1. Fetch latest feeds and compile JSON data
python aggregator.py

# 2. Build static website
python build.py

# 3. Preview locally
# Open dist/index.html in any browser
```

---

## 🚢 How to Deploy to GitHub (5 Minutes)

1. Create a new repository on [GitHub](https://github.com/new) (e.g., `devstack-deals`).
2. Initialize and push this directory:
   ```bash
   git init
   git add .
   git commit -m "feat: initial deals aggregator release"
   git branch -M main
   git remote add origin https://github.com/<your-username>/devstack-deals.git
   git push -u origin main
   ```
3. Enable GitHub Pages:
   - Go to **Settings > Pages** in your GitHub repo.
   - Under **Build and deployment > Source**, select **GitHub Actions**.
4. The workflow will run immediately, and your live site will be accessible at:
   `https://<your-username>.github.io/devstack-deals/`
