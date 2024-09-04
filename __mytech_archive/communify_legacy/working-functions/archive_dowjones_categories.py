######################################
        ######   BEGIN BUSINESS LOGIC  #######
        ######################################
        
        #The entire taxonomy cannot be downloaded. It must be obtained by category and changes constantly
        # This sequence will create the entire taxonomy by category and save it to a JSON file.
        self.complete_taxonomy_dict = {}
        # Instantiate the complete taxonomy dictionary
        complete_dj_taxonomy_path = f'{self.IO_FOLDER_PATH}/complete_category_taxonomy_{self.unique_run_id}.json'
        with open(complete_dj_taxonomy_path, 'w') as f:
            f.write(json.dumps(self.complete_taxonomy_dict, indent=4))

        # The DJID Taxonomy API uses categories as dimensions to classify its content. Some categories compliment others.
        # For example, the Industries category is part of the classifying dimensions for the Companies category.
        # see https://developer.dowjones.com/site/docs/factiva_apis/factiva_workflow_apis_rest/factiva_news_search/factiva_djid_taxonomy_api/index.gsp#currToc
        for category_key in self.official_taxonomy_dict .keys():
            
            if self.official_taxonomy_dict[category_key].get("endpoint"):
                # If true, this category has sub-categories:
                # We need to get the sub-categories and add them to the complete taxonomy
                # As of the time this code was writte, the Categories are as follows:
                # Author    (NO sub-categories)     (Only searchable, CANNOT download the entire list)  (Handled differently)
                # Company   (NO sub-categories)     (Only searchable, CANNOT download the entire list)  (Handled differently)
                # |-----|
                # Language  (NO sub-categories)     (CAN download the entire list)
                # |-----|
                # Industry  (HAS sub-categories)    (CAN download the entire list)
                # Subject   (HAS sub-categories)    (CAN download the entire list)
                # Region    (HAS sub-categories)    (CAN download the entire list)
                # |-----|
                # Source    (HAS sub-categories)    (CANNOT download the entire list)

                category_taxonomy_dict = get_category_taxonomy(
                    category=category_key, endpoint=self.official_taxonomy_dict[category_key].get("endpoint"))

                with open(complete_dj_taxonomy_path, 'r+') as f:
                    current_text = f.read()
                    current_dict = json.loads(current_text)
                    current_dict[category_key] = category_taxonomy_dict
                    f.write(json.dumps(current_dict, indent=4))

                # Add the category to the complete taxonomy
                self.complete_taxonomy_dict[category_key] = {}
                attribute_dictionary_name = self.official_taxonomy_dict [category_key].get(
                    "category").replace("factiva-", "")

                if isinstance(category_taxonomy_dict.get('data'), list):
                    # the below supports language and sets category_data_items to be a list of dicts
                    category_data_items = category_taxonomy_dict.get('data')
                else:
                    if isinstance(category_taxonomy_dict.get('data'), dict):

                        # The below supports industry and sets category_data_items to be a list of dicts
                        category_data_items = category_taxonomy_dict.get('data').get(
                            "attributes").get(attribute_dictionary_name)

                for category_data_item in category_data_items:
                    if category_data_item is not None:
                        if category_data_item.get('code'):
                            self.complete_taxonomy_dict[category_key][category_data_item.get(
                                'code')] = category_data_item
                        elif category_data_item.get('id'):
                            self.complete_taxonomy_dict[category_key][category_data_item.get(
                                'id')] = category_data_item

                # complete_dj_taxonomy_dict should now be fully populated for the first level of categories.
                # Which is: Language, Industry, Subject, Region
                # Language is entirely complete. The others have sub-categories and which are handled next.

                if self.official_taxonomy_dict[category_key].get("children"):
                    # Industry  (HAS sub-categories)    (CAN download the entire list)
                    # Subject   (HAS sub-categories)    (CAN download the entire list)
                    # Region    (HAS sub-categories)    (CAN download the entire list)

                    # Note: Source has children but a full list cannot be downloaded so it is not handled here.
                    # Source    (HAS sub-categories)    (CANNOT download the entire list)

                    sub_category_connection_dict = self.official_taxonomy_dict [category_key].get(
                        "children")

                    for sub_category_key in category_taxonomy_dict.get("data"):
                        # Note: Below get_sub_category_taxonomy is a modifying wrapper for get_category_taxonomy
                        with open(f'{self.IO_folder}/sub_category_log_{self.unique_run_id}.text', 'a') as f:
                            f.write(
                                f"Beginning attempt to get sub-category {sub_category_key.get('id','MISSING')} for category {category_key}.\n")
                        sub_category_taxonomy_dict = get_sub_category_taxonomy(
                            sub_category=sub_category_key.get("id", ""), endpoint=self.official_taxonomy_dict[category_key].get("endpoint"))

                        if isinstance(sub_category_taxonomy_dict, str):
                            # If the sub-category is not a list, it's an error message
                            print(sub_category_taxonomy_dict)
                            with open(f'{self.IO_folder}/sub_category_log_{self.unique_run_id}.text', 'a') as f:
                                f.write(sub_category_taxonomy_dict)
                        else:
                            # Save the sub-category to a JSON file
                            with open(f'{self.IO_folder}/category_taxonomy_{category_key}_{sub_category_key.get("id","MISSING")}.json', 'w') as f:
                                f.write(json.dumps(
                                    sub_category_taxonomy_dict, indent=4))

                            # Add the subcategories whichis delivered as a list to the complete taxonomy
                            for sub_category_data_item in sub_category_taxonomy_dict.get("data"):
                                self.complete_taxonomy_dict[category_key][sub_category_key.get(
                                    "id", "")] = sub_category_data_item

                            with open(f'{self.IO_folder}/sub_category_log_{self.unique_run_id}.text', 'a') as f:
                                f.write(
                                    f"Successfully completed attempt to get sub-category {sub_category_key.get('id','MISSING')} for category {category_key}.\n")

                    # End of Sub-Category Logic:

                else:
                    # Code to handle:
                    # Author    (NO sub-categories)     (Only searchable, cannot download the entire list)  (Handled differently)
                    # Company   (NO sub-categories)     (Only searchable, cannot download the entire list)  (Handled differently)
                    # Source    (HAS sub-categories)    (CANNOT download the entire list)
                    print(f'{category_key} is handled at run time and not in this loop.')