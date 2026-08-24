import { useEffect, useMemo, useState } from "react";
import { Pencil, Plus, Trash2, UserRound, UsersRound, X } from "lucide-react";

import api from "../services/api";

const EMPTY_FORM = {
  display_name: "",
  email: "",
  password: "",
  role: "USER",
};

function UserManagement() {
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const loggedInEmail = useMemo(() => {
    try {
      const token = localStorage.getItem("token");
      if (!token) return "";
      const payload = JSON.parse(atob(token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/")));
      return payload.email || "";
    } catch {
      return "";
    }
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      setError("");
      const response = await api.get("/admin/users");
      setUsers(response.data);
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Unable to load users.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const resetForm = () => {
    setForm(EMPTY_FORM);
    setEditingId(null);
    setError("");
  };

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setSuccess("");

    if (!form.display_name.trim() || !form.email.trim()) {
      setError("Name and email are required.");
      return;
    }

    if (!editingId && form.password.length < 8) {
      setError("Password must contain at least 8 characters.");
      return;
    }

    if (editingId && form.password && form.password.length < 8) {
      setError("New password must contain at least 8 characters.");
      return;
    }

    try {
      setSaving(true);

      if (editingId) {
        const payload = {
          display_name: form.display_name.trim(),
          email: form.email.trim(),
          role: form.role,
        };

        if (form.password) {
          payload.password = form.password;
        }

        await api.put(`/admin/users/${editingId}`, payload);
        setSuccess("User account updated successfully.");
      } else {
        await api.post("/admin/users", {
          display_name: form.display_name.trim(),
          email: form.email.trim(),
          password: form.password,
          role: form.role,
        });
        setSuccess("User account created successfully.");
      }

      resetForm();
      await loadUsers();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Unable to save the user account.");
    } finally {
      setSaving(false);
    }
  };

  const startEdit = (user) => {
    setEditingId(user.id);
    setForm({
      display_name: user.display_name,
      email: user.email,
      password: "",
      role: user.role,
    });
    setError("");
    setSuccess("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const deleteUser = async (user) => {
    const confirmed = window.confirm(
      `Delete ${user.display_name} (${user.email})? This action cannot be undone.`
    );

    if (!confirmed) return;

    try {
      setError("");
      setSuccess("");
      await api.delete(`/admin/users/${user.id}`);
      setSuccess("User account deleted successfully.");

      if (editingId === user.id) {
        resetForm();
      }

      await loadUsers();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Unable to delete the user account.");
    }
  };

  const formatDate = (value) => {
    if (!value) return "-";
    return new Date(value).toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "2-digit",
    });
  };

  return (
    <>
      <div className="page-heading">
        <div>
          <p className="page-label">ADMINISTRATION</p>
          <h1>User Management</h1>
          <p>Create and manage DeployPilot AI administrator and user accounts.</p>
        </div>

        <div className="live-status">
          <UsersRound size={16} />
          {users.length} account{users.length === 1 ? "" : "s"}
        </div>
      </div>

      <div className="user-management-grid">
        <section className="content-card user-form-card">
          <div className="card-heading">
            <div>
              <h2>{editingId ? "Update Account" : "Create Account"}</h2>
              <p>
                {editingId
                  ? "Edit account details. Leave the password empty to keep the current password."
                  : "Create a new administrator or standard user account."}
              </p>
            </div>

            {editingId && (
              <button className="small-icon-button" type="button" onClick={resetForm} title="Cancel edit">
                <X size={17} />
              </button>
            )}
          </div>

          <form onSubmit={handleSubmit}>
            <div className="user-form-fields">
              <div className="form-field">
                <label htmlFor="display_name">Full Name</label>
                <input
                  id="display_name"
                  name="display_name"
                  value={form.display_name}
                  onChange={handleChange}
                  placeholder="e.g. Project User"
                />
              </div>

              <div className="form-field">
                <label htmlFor="email">Email Address</label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  value={form.email}
                  onChange={handleChange}
                  placeholder="user@deploypilot.ai"
                />
              </div>

              <div className="form-field">
                <label htmlFor="password">
                  {editingId ? "New Password (optional)" : "Password"}
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  value={form.password}
                  onChange={handleChange}
                  placeholder={editingId ? "Leave blank to keep current password" : "Minimum 8 characters"}
                />
              </div>

              <div className="form-field">
                <label htmlFor="role">Account Role</label>
                <select id="role" name="role" value={form.role} onChange={handleChange}>
                  <option value="USER">User</option>
                  <option value="ADMIN">Administrator</option>
                </select>
              </div>
            </div>

            <button className="primary-button user-submit-button" type="submit" disabled={saving}>
              {editingId ? <Pencil size={17} /> : <Plus size={17} />}
              {saving ? "Saving..." : editingId ? "Update Account" : "Create Account"}
            </button>

            {editingId && (
              <button className="secondary-button user-cancel-button" type="button" onClick={resetForm}>
                Cancel
              </button>
            )}
          </form>
        </section>

        <section className="content-card user-list-card">
          <div className="card-heading">
            <div>
              <h2>Accounts</h2>
              <p>Administrators can create, update and delete DeployPilot AI accounts.</p>
            </div>
          </div>

          {error && <div className="form-error user-message">{error}</div>}
          {success && <div className="form-success user-message">{success}</div>}

          {loading ? (
            <div className="empty-state">
              <h3>Loading accounts...</h3>
            </div>
          ) : users.length === 0 ? (
            <div className="empty-state">
              <UserRound size={30} />
              <h3>No accounts found</h3>
              <p>Create your first account using the form.</p>
            </div>
          ) : (
            <div className="table-wrapper">
              <table className="user-table">
                <thead>
                  <tr>
                    <th>User</th>
                    <th>Role</th>
                    <th>Status</th>
                    <th>Created</th>
                    <th>Actions</th>
                  </tr>
                </thead>

                <tbody>
                  {users.map((user) => {
                    const isSelf = user.email.toLowerCase() === loggedInEmail.toLowerCase();

                    return (
                      <tr key={user.id}>
                        <td>
                          <div className="user-cell">
                            <div className="table-avatar">{user.display_name.charAt(0).toUpperCase()}</div>
                            <div>
                              <strong>{user.display_name}</strong>
                              <span>{user.email}</span>
                            </div>
                          </div>
                        </td>
                        <td>
                          <span className={`role-badge ${user.role.toLowerCase()}`}>
                            {user.role === "ADMIN" ? "Administrator" : "User"}
                          </span>
                        </td>
                        <td>
                          <span className={user.is_active ? "status allow" : "status block"}>
                            {user.is_active ? "Active" : "Inactive"}
                          </span>
                        </td>
                        <td>{formatDate(user.created_at)}</td>
                        <td>
                          <div className="table-actions">
                            <button className="table-action edit-action" type="button" onClick={() => startEdit(user)}>
                              <Pencil size={15} />
                              Edit
                            </button>

                            <button
                              className="table-action delete-action"
                              type="button"
                              onClick={() => deleteUser(user)}
                              disabled={isSelf}
                              title={isSelf ? "You cannot delete your own account" : "Delete account"}
                            >
                              <Trash2 size={15} />
                              Delete
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>
    </>
  );
}

export default UserManagement;
