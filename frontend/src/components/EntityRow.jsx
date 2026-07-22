function EntityRow({ title, items }) {
    return (
        <div className="entity-row">
            <strong>{title}</strong>

            <div className="entity-list">
                {items.length ? (
                    items.map((item, index) => (
                        <span key={index} className="entity-chip">
                            {item}
                        </span>
                    ))
                ) : (
                    <span className="entity-empty">
                        None
                    </span>
                )}
            </div>
        </div>
    );
}

export default EntityRow;