import { useNavigate } from "react-router-dom";
import {
    ArrowRight,
    AlertTriangle,
    CircleAlert,
    CheckCircle
} from "lucide-react";

import "./EmailsCard.css";

function EmailCard({ id, subject, category, priority, summary }) {

    const navigate = useNavigate();

    function getPriority(priority) {

        if (priority >= 70)
            return {
                text: "High",
                color: "#EF4444",
                icon: <AlertTriangle size={16} />
            };

        if (priority >= 40)
            return {
                text: "Medium",
                color: "#F59E0B",
                icon: <CircleAlert size={16} />
            };

        return {
            text: "Low",
            color: "#10B981",
            icon: <CheckCircle size={16} />
        };
    }

    const priorityInfo = getPriority(priority);

    return (

        <div
            className="email-card"
            onClick={() => navigate(`/emails/${id}`)}
        >

            <div className="email-header">

                <h3>{subject}</h3>

                <span
                    className="priority-badge"
                    style={{ background: priorityInfo.color }}
                >
                    {priorityInfo.icon}
                    {priorityInfo.text}
                </span>

            </div>

            <span className="category-chip">
                {category}
            </span>

            <p className="summary">
                {summary}
            </p>

            <div className="email-footer">

                <span>
                    Priority Score : {priority}
                </span>

                <ArrowRight size={18} />

            </div>

        </div>

    );

}

export default EmailCard;