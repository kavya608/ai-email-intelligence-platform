import "./AnalyticsCard.css";

function AnalyticsCard({ title, children }) {
    return (
        <div className="analytics-card">

            <h3>{title}</h3>

            {children}

        </div>
    );
}

export default AnalyticsCard;