"""
Advanced API integration examples for divine-typed-requests library.

This example demonstrates real-world usage patterns including:
- Complex nested type validation
- API client class patterns
- Error handling strategies
- Data transformation
- Retry logic
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Any, TypedDict

from type_enforcer import ValidationError

from typed_requests import NetworkingManager

# ===== GitHub API Type Definitions =====


class GitHubUser(TypedDict):
    login: str
    id: int
    avatar_url: str
    url: str
    name: str | None
    company: str | None
    blog: str | None
    location: str | None
    email: str | None
    bio: str | None
    public_repos: int
    followers: int
    following: int
    created_at: str


class GitHubRepository(TypedDict):
    id: int
    name: str
    full_name: str
    private: bool
    owner: GitHubUser
    html_url: str
    description: str | None
    fork: bool
    url: str
    created_at: str
    updated_at: str
    pushed_at: str
    clone_url: str
    size: int
    stargazers_count: int
    watchers_count: int
    language: str | None
    has_issues: bool
    has_projects: bool
    has_wiki: bool
    has_pages: bool
    open_issues_count: int
    archived: bool
    disabled: bool
    visibility: str
    default_branch: str


class GitHubIssue(TypedDict):
    id: int
    number: int
    title: str
    user: GitHubUser
    state: str
    body: str | None
    created_at: str
    updated_at: str
    closed_at: str | None
    html_url: str
    labels: list[dict[str, Any]]
    assignees: list[GitHubUser]
    comments: int


# ===== API Client Class =====


class GitHubAPIClient:
    """
    A comprehensive GitHub API client demonstrating advanced usage patterns.
    """

    def __init__(self, token: str | None = None):
        self.base_url = "https://api.github.com"
        self.manager = NetworkingManager()
        self.token = token
        self.headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "divine-typed-requests-Example/1.0"}

        if token:
            self.headers["Authorization"] = f"token {token}"

    async def __aenter__(self):
        """Async context manager entry."""
        await self.manager.startup()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.manager.shutdown()

    async def get_user(self, username: str) -> GitHubUser:
        """
        Get a GitHub user by username with type validation.

        Args:
            username: GitHub username

        Returns:
            GitHubUser: Validated user data

        Raises:
            ValidationError: If response doesn't match expected structure
        """
        try:
            response = await self.manager.get(
                f"{self.base_url}/users/{username}", headers=self.headers, expected_type=GitHubUser
            )
            return response.data
        except ValidationError as e:
            print(f"User data validation failed: {e}")
            raise
        except Exception as e:
            print(f"Failed to fetch user {username}: {e}")
            raise

    async def get_user_repositories(self, username: str) -> list[GitHubRepository]:
        """
        Get repositories for a user with type validation.

        Args:
            username: GitHub username

        Returns:
            List[GitHubRepository]: Validated repository data
        """
        try:
            response = await self.manager.get(
                f"{self.base_url}/users/{username}/repos", headers=self.headers, expected_type=list[GitHubRepository]
            )
            return response.data
        except ValidationError as e:
            print(f"Repository data validation failed: {e}")
            raise
        except Exception as e:
            print(f"Failed to fetch repositories for {username}: {e}")
            raise

    async def get_repository_issues(self, owner: str, repo: str, state: str = "open") -> list[GitHubIssue]:
        """
        Get issues for a repository with type validation.

        Args:
            owner: Repository owner
            repo: Repository name
            state: Issue state (open, closed, all)

        Returns:
            List[GitHubIssue]: Validated issue data
        """
        try:
            response = await self.manager.get(
                f"{self.base_url}/repos/{owner}/{repo}/issues",
                headers=self.headers,
                params={"state": state},
                expected_type=list[GitHubIssue],
            )
            return response.data
        except ValidationError as e:
            print(f"Issue data validation failed: {e}")
            raise
        except Exception as e:
            print(f"Failed to fetch issues for {owner}/{repo}: {e}")
            raise

    async def search_repositories(self, query: str, sort: str = "stars") -> dict[str, Any]:
        """
        Search repositories using GitHub's search API.

        Args:
            query: Search query
            sort: Sort order (stars, forks, updated)

        Returns:
            Dict containing search results
        """
        try:
            response = await self.manager.get(
                f"{self.base_url}/search/repositories",
                headers=self.headers,
                params={"q": query, "sort": sort},
                expected_type=dict[str, Any],
            )
            return response.data
        except Exception as e:
            print(f"Failed to search repositories: {e}")
            raise


# ===== Advanced Usage Examples =====


async def user_profile_example():
    """Example of fetching and displaying user profile data."""
    print("=== User Profile Example ===")

    async with GitHubAPIClient() as client:
        try:
            # Fetch user data
            user = await client.get_user("octocat")

            print(f"User: {user['login']}")
            print(f"Name: {user['name']}")
            print(f"Company: {user['company']}")
            print(f"Location: {user['location']}")
            print(f"Public Repos: {user['public_repos']}")
            print(f"Followers: {user['followers']}")
            print(f"Following: {user['following']}")

        except Exception as e:  # noqa: BLE001
            print(f"Error fetching user profile: {e}")


async def repository_analysis_example():
    """Example of analyzing user repositories."""
    print("\n=== Repository Analysis Example ===")

    async with GitHubAPIClient() as client:
        try:
            # Fetch repositories
            repos = await client.get_user_repositories("octocat")

            print(f"Found {len(repos)} repositories")
            print("\nTop 5 repositories by stars:")

            # Sort by stars and show top 5
            sorted_repos = sorted(repos, key=lambda r: r["stargazers_count"], reverse=True)
            for i, repo in enumerate(sorted_repos[:5]):
                print(f"{i + 1}. {repo['name']}: {repo['stargazers_count']} stars")
                print(f"   Language: {repo['language']}")
                print(f"   Description: {repo['description']}")
                print()

        except Exception as e:  # noqa: BLE001
            print(f"Error analyzing repositories: {e}")


async def issue_tracking_example():
    """Example of tracking issues in a repository."""
    print("\n=== Issue Tracking Example ===")

    async with GitHubAPIClient() as client:
        try:
            # Fetch issues from a popular repository
            issues = await client.get_repository_issues("microsoft", "vscode")

            print(f"Found {len(issues)} open issues")
            print("\nRecent issues:")

            for i, issue in enumerate(issues[:3]):  # Show first 3 issues
                print(f"{i + 1}. #{issue['number']}: {issue['title']}")
                print(f"   Created by: {issue['user']['login']}")
                print(f"   Comments: {issue['comments']}")
                print(f"   Labels: {[label['name'] for label in issue['labels']]}")
                print()

        except Exception as e:  # noqa: BLE001
            print(f"Error tracking issues: {e}")


async def search_and_analyze_example():
    """Example of searching repositories and analyzing results."""
    print("\n=== Search and Analysis Example ===")

    async with GitHubAPIClient() as client:
        try:
            # Search for Python machine learning repositories
            results = await client.search_repositories("language:python machine learning")

            print(f"Found {results['total_count']} repositories")
            print("\nTop 3 results:")

            for i, repo in enumerate(results["items"][:3]):
                print(f"{i + 1}. {repo['full_name']}")
                print(f"   Stars: {repo['stargazers_count']}")
                print(f"   Description: {repo['description']}")
                print(f"   Language: {repo['language']}")
                print(f"   Last updated: {repo['updated_at']}")
                print()

        except Exception as e:  # noqa: BLE001
            print(f"Error searching repositories: {e}")


async def error_handling_and_retry_example():
    """Example of advanced error handling and retry logic."""
    print("\n=== Error Handling and Retry Example ===")

    async def fetch_with_retry(client: GitHubAPIClient, url: str, max_retries: int = 3):
        """Fetch data with retry logic."""
        for attempt in range(max_retries):
            try:
                response = await client.manager.get(url, headers=client.headers)
                return response.json()
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2**attempt)  # Exponential backoff

    async with GitHubAPIClient() as client:
        try:
            # Try to fetch data with retry logic
            data = await fetch_with_retry(client, f"{client.base_url}/users/octocat")
            print(f"Successfully fetched user data: {data['login']}")

        except Exception as e:  # noqa: BLE001
            print(f"Failed after all retries: {e}")


async def data_transformation_example():
    """Example of transforming API data into custom structures."""
    print("\n=== Data Transformation Example ===")

    @dataclass
    class UserSummary:
        username: str
        display_name: str
        repo_count: int
        total_stars: int
        primary_language: str
        join_date: datetime

    async def create_user_summary(username: str) -> UserSummary:
        """Create a user summary from GitHub API data."""
        async with GitHubAPIClient() as client:
            # Fetch user and repository data
            user = await client.get_user(username)
            repos = await client.get_user_repositories(username)

            # Calculate statistics
            total_stars = sum(repo["stargazers_count"] for repo in repos)
            languages = [repo["language"] for repo in repos if repo["language"]]
            primary_language = max(set(languages), key=languages.count) if languages else "Unknown"

            # Create summary
            return UserSummary(
                username=user["login"],
                display_name=user["name"] or user["login"],
                repo_count=len(repos),
                total_stars=total_stars,
                primary_language=primary_language,
                join_date=datetime.fromisoformat(user["created_at"].replace("Z", "+00:00")),
            )

    try:
        summary = await create_user_summary("octocat")
        print(f"User Summary for {summary.username}:")
        print(f"  Display Name: {summary.display_name}")
        print(f"  Repositories: {summary.repo_count}")
        print(f"  Total Stars: {summary.total_stars}")
        print(f"  Primary Language: {summary.primary_language}")
        print(f"  Member since: {summary.join_date.strftime('%Y-%m-%d')}")

    except Exception as e:  # noqa: BLE001
        print(f"Error creating user summary: {e}")


# ===== Main Example Function =====


async def main():
    """Run all advanced examples."""
    print("Divine Requests Library - Advanced API Integration Examples")
    print("=" * 60)

    try:
        await user_profile_example()
        await repository_analysis_example()
        await issue_tracking_example()
        await search_and_analyze_example()
        await error_handling_and_retry_example()
        await data_transformation_example()

        print("\n" + "=" * 60)
        print("All advanced examples completed!")

    except Exception as e:  # noqa: BLE001
        print(f"Error in main: {e}")


if __name__ == "__main__":
    asyncio.run(main())
