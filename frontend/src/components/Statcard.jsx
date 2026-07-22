import "./StatCard.css";

function StatCard({ title, value, icon, color }) {

    return (

        <div
            className="stat-card"
            style={{ borderTop: `5px solid ${color}` }}
        >

            <div
                className="stat-icon"
                style={{ backgroundColor: color }}
            >
                {icon}
            </div>

            <div className="stat-content">

                <h2>{value}</h2>

                <h3>{title}</h3>

            </div>

        </div>

    );

}

export default StatCard;