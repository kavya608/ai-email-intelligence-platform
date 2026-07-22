import { useState, useEffect } from "react";
import axios from "../api/axios";
import EmailCard from "../components/EmailCard";
import "../styles/Emails.css";
import { Search } from "lucide-react";
import Loader from "../components/Loader";

function Emails() {

    const [emails, setEmails] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");
    const [category, setCategory] = useState("All");
    const [sortBy, setSortBy] = useState("");
    const [currentPage, setCurrentPage] = useState(1);
    const [totalEmails, setTotalEmails] = useState(0);

    useEffect(() => {

    async function fetchEmails() {

        const params = new URLSearchParams();

        params.append("page", currentPage);
        params.append("limit", 5);

        if (category !== "All") {
            params.append("category", category);
        }

        if (search.trim() !== "") {
            params.append("search", search);
        }

        if (sortBy !== "") {
            params.append("sort", sortBy);
        }

        const response = await axios.get(
            `/emails?${params.toString()}`
        );

        setEmails(response.data.emails);
        setTotalEmails(response.data.total);
        if (loading) {
            setLoading(false);
        }

    }

    fetchEmails();

}, [currentPage, category, search, sortBy]);
    const filteredEmails = emails;
    if (loading) {
        return <Loader />;
    }

    return (

        <div>
            <h1 className="page-title">
                📬 Emails
            </h1>

            <p className="page-subtitle">
                Browse, search and manage AI processed emails.
            </p>

            <div className="search-filter">

                <div className="search-box">

                    <Search size={18} className="search-icon" />

                    <input
                        type="text"
                        placeholder="Search emails..."
                        className="search-input"
                        value={search}
                        onChange={(e) => {
                            setSearch(e.target.value);
                            setCurrentPage(1);
                        }}
                    />

                </div>
                <select
                    className="category-select"
                    value={category}
                    onChange={(e) => {setCategory(e.target.value); setCurrentPage(1);}}
                >
                    <option value="All">All</option>
                    <option value="Spam-like">Spam-like</option>
                    <option value="Meeting">Meeting</option>
                    <option value="Urgent">Urgent</option>
                    <option value="Action Needed">Action Needed</option>
                    <option value="Informational">Informational</option>

                </select>

                <select
                    className="category-select"
                    value={sortBy}
                    onChange={(e) => {setSortBy(e.target.value); setCurrentPage(1);}}
                >

                    <option value="">Sort By</option>

                    <option value="priority-high">
                        Priority High → Low
                    </option>

                    <option value="priority-low">
                        Priority Low → High
                    </option>

                    <option value="subject-asc">
                        Subject A → Z
                    </option>

                    <option value="subject-desc">
                        Subject Z → A
                    </option>

                </select>

            </div>

            {filteredEmails.length === 0 ? (

                <div className="empty-state">

                    <div className="empty-icon">
                        📭
                    </div>

                    <h2>No Emails Found</h2>

                    <p>
                        We couldn't find any emails matching your search or filters.
                    </p>

                </div>

            ) : (

                filteredEmails.map((email) => (

                    <div key={email.id}>

                        <EmailCard
                            id={email.id}
                            subject={email.subject}
                            category={email.category}
                            priority={email.priority_score}
                            summary={email.summary}
                        />

                    </div>

                ))

            )}

            {filteredEmails.length > 0 && (

            <div className="pagination">

                <button
                    onClick={() => setCurrentPage(currentPage - 1)}
                    disabled={currentPage === 1}
                >
                    ← Previous
                </button>

                <span className="page-number">
                    Page {currentPage}
                </span>

                <button
                    onClick={() => setCurrentPage(currentPage + 1)}
                    disabled={currentPage * 5 >= totalEmails}
                >
                    Next →
                </button>

            </div>

)}

        </div>

    );
}

export default Emails;