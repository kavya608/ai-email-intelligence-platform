import EntityRow from "../components/EntityRow";
import { useParams } from "react-router-dom";
import { useState, useEffect } from "react";
import API from "../api/axios";
import "../styles/EmailDetails.css";
import Section from "../components/sections";

function EmailDetails() {
    const { id } = useParams()
    const[email, setEmail] = useState(null)
    
    useEffect(()=> {
        async function fetchEmail() {

        const response = await API.get(`/emails/${id}`);
        setEmail(response.data);

        console.log(response.data);

    }

    fetchEmail();
    },[]);
    if (!email) {
    return <h2>Loading Email...</h2>;
    }

    return (
    <div className="email-card">

        <h2>{email.subject}</h2>

        <div className="detail-row">

            <strong>Category</strong>

            <span>{email.category}</span>

        </div>

        <div className="detail-row">

            <strong>Priority</strong>

            <span className="priority-badge">

                {email.priority_score}

            </span>
        </div>

        <Section

            title="📝 Summary"

            content={email.summary}

        />
        <Section

            title="📄 Body"

            content={email.body}

        />

        <Section
            title="✅ Action Items"
            content={email.action_items || "No action items found."}
        />

        <h3>🧠 Extracted Entities</h3>

        <EntityRow
            title="👤 People"
            items={email.entities.people}
        />

        <EntityRow
            title="📍 Locations"
            items={email.entities.locations}
        />

        <EntityRow
            title="🏢 Organizations"
            items={email.entities.organizations}
        />

        <EntityRow
            title="💰 Money"
            items={email.entities.money}
        />

        <EntityRow
            title="📅 Dates"
            items={email.entities.dates}
        />
    </div>
    
);

}

export default EmailDetails;