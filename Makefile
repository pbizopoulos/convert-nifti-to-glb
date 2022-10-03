.POSIX:

.PHONY: clean help

artifacts_dir=artifacts
container_engine=docker # For podman first execute `printf 'unqualified-search-registries=["docker.io"]\n' > /etc/containers/registries.conf.d/docker.conf`
work_dir=/work

$(artifacts_dir)/code-run: $(artifacts_dir)/cert.pem .gitignore package-lock.json ## Run local server.
	ARTIFACTSDIR=$(artifacts_dir) npx http-server -S -C $(artifacts_dir)/cert.pem -K $(artifacts_dir)/key.pem
	touch $(artifacts_dir)/code-run

.gitignore:
	printf '$(artifacts_dir)/\nnode_modules/\npackage-lock.json\n' > .gitignore

clean: ## Remove dependent directories.
	rm -rf $(artifacts_dir)/ node_modules/ package-lock.json

help: ## Show all commands.
	@sed -n '/sed/d; s/\$$(artifacts_dir)/$(artifacts_dir)/g; /##/p' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.* ## "}; {printf "%-30s# %s\n", $$1, $$2}'

package-lock.json: package.json
	npm install

package.json:
	printf '{}\n' > package.json

$(artifacts_dir):
	mkdir $(artifacts_dir)

$(artifacts_dir)/cert.pem: $(artifacts_dir)
	openssl req -newkey rsa:2048 -subj "/C=US/ST=US/L=Washington/O=.../OU=.../CN=.../emailAddress=..." -new -nodes -x509 -days 3650 -keyout $(artifacts_dir)/key.pem -out $(artifacts_dir)/cert.pem

$(artifacts_dir)/artifacts/masks.nii: $(artifacts_dir) ## Download masks.nii.
	git clone https://github.com/pbizopoulos/semi-automatic-annotation $(artifacts_dir)
	make -C $(artifacts_dir)
