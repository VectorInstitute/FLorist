import { ReactElement } from "react/React";

export default function NewJob(): ReactElement {
    return (
        <div className="col-6 text-end">
            <NewJobButton />
            <div className="fixed-plugin text-start">
                <div className="card shadow-lg">
                    <NewJobHeader />

                    <hr className="horizontal dark my-1" />

                    <NewJobForm />
                </div>
            </div>
        </div>
    );
}

export function NewJobButton(): ReactElement {
    return (
        <a className="fixed-plugin-button btn bg-gradient-primary mb-0">
            <i className="material-icons text-sm">add</i>
            &nbsp;&nbsp;New Job
        </a>
    );
}

export function NewJobHeader(): ReactElement {
    return (
        <div className="card-header pb-0 pt-3">
            <div className="float-start">
                <h5 className="mt-3 mb-0">New Job</h5>
                <p>Create a new FL training job.</p>
            </div>
            <div className="float-end mt-4">
                <button className="btn btn-link text-dark p-0 fixed-plugin-close-button">
                    <i className="material-icons">clear</i>
                </button>
            </div>
        </div>
    );
}

export function NewJobForm(): ReactElement {
    return (
        <div className="card-body pt-sm-3 pt-0">
            <form>
                <div className="input-group input-group-outline">
                    <label className="form-label">Model</label>
                    <input type="text" className="form-control" />
                </div>
            </form>
        </div>
    );
}
