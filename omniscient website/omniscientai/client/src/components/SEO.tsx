import { Helmet } from "react-helmet-async";

interface SEOProps {
    title?: string;
    description?: string;
    image?: string;
    article?: boolean;
}

export default function SEO({ title, description, image, article }: SEOProps) {
    const siteName = "OmniscientAI";
    const fullTitle = title ? `${title} | ${siteName}` : siteName;
    const defaultDescription = "Vendor-neutral AI training workshops and consulting for Melbourne SMEs. Transform your team with practical AI skills.";
    const defaultImage = "https://omniscientai.io/og-image.jpg"; // Placeholder for now

    return (
        <Helmet>
            <title>{fullTitle}</title>
            <meta name="description" content={description || defaultDescription} />
            <link rel="canonical" href={window.location.href} />

            {/* Open Graph */}
            <meta property="og:site_name" content={siteName} />
            <meta property="og:title" content={fullTitle} />
            <meta property="og:description" content={description || defaultDescription} />
            <meta property="og:image" content={image || defaultImage} />
            <meta property="og:type" content={article ? "article" : "website"} />
            <meta property="og:url" content={window.location.href} />

            {/* Twitter Card */}
            <meta name="twitter:card" content="summary_large_image" />
            <meta name="twitter:title" content={fullTitle} />
            <meta name="twitter:description" content={description || defaultDescription} />
            <meta name="twitter:image" content={image || defaultImage} />
        </Helmet>
    );
}
